from __future__ import annotations

import logging
from io import BytesIO
from typing import Iterable

from environ_odoo_config.environ import new_environ
from minio.deleteobjects import DeleteObject
from minio.error import S3Error
from typing_extensions import Self

from odoo.addons.odoo_filestore_s3.env_config import FilestoreS3EnvConfig

_logger = logging.getLogger(__name__)


class S3OdooBucketInfo:
    def __init__(self, name: str, sub_dir_name: str | None = None, checklist_dir: str | None = None):
        """
        Represente la configurtation d'un bucket S3
        :param name: Le nom du bucket : obligatoire
        :param sub_dir_name: Non d'un dossier inclut lors de la création d'une clef
        :param checklist_dir: Nom du dossier pour faire la gestion des fichiers à supprimer
        """
        assert name
        self.name = name
        self.sub_dir_name = sub_dir_name
        self.checklist_dir = checklist_dir or "checklist"

    def get_key(self, *file_paths: str) -> str:
        """
        Retourne la clef pour la paire db_name et file_name

        Si la connexion (self.conn) à été créée avec **sub_dir_by_db** à Vrai alors le format sera <db_name>/<file_name>
        Sinon uniquement file_names sera retourné séparé par des '/'
        :param file_paths: un tableau de 1 ou n constituant le chemain sous first-dir
        du fichier dans le bucket, supprime les valeur <False>
        :return: self.sub_dir_name/*file_paths ir sub_dir_name is provided
        """
        keys = [f for f in file_paths if f]
        if bool(self.sub_dir_name):
            keys.insert(0, self.sub_dir_name)
        return "/".join(keys)


class _S3Odoo:
    def __init__(self):
        self._config = FilestoreS3EnvConfig(new_environ())

    def from_env(self, db_name: str = None) -> "S3Filestore":
        if self._config.sub_dir and not db_name:
            raise ValueError("db_name not provided but your environ variable to required it are set")
        dbname = db_name if self._config.sub_dir else None
        return S3Filestore(self._config, db_name=dbname)

    def connect_from_env(self) -> "S3Filestore":
        """
        Créer une connexion au S3 sans prendre en compte le nom de la base de donnée.
        Il faudra donc l'ajouter dans le path de chaque fichier envoyé
        :return: Un connexion au S3 distant depuis les variable d'environement
        """
        return S3Filestore(self._config, db_name=None)

    def reload_env_config(self) -> Self:
        self._config = FilestoreS3EnvConfig(new_environ())
        return self


S3Odoo = _S3Odoo()


class S3Filestore:
    def __init__(self, config: FilestoreS3EnvConfig, *, db_name: str | None = None):
        self.conn = config
        self.bucket = S3OdooBucketInfo(name=config.bucket_name, sub_dir_name=db_name)

    def get_key(self, *file_paths: str) -> str:
        """
        Voir S3OdooBucketInfo#get_key
        :param file_paths: le path du fichier dans une liste
        :return: le path du fichier
        """
        return self.bucket.get_key(*file_paths)

    def bucket_exist(self) -> bool:
        """
        :return: Vrai si le bucket existe
        """
        return self.conn.s3_session.bucket_exists(self.bucket.name)

    def delete_bucket(self) -> bool:
        """
        Supprime le bucket founit au debut de l'instanciation
        :return: Vrai si la suppression à reussi
        """
        try:
            s3_session = self.conn.s3_session
        except Exception as e:
            _logger.error(
                "S3: delete_bucket Was not able to connect to S3 (%s)",
                e.message,
                exc_info=e,
            )
            return False
        try:
            s3_session.remove_bucket(self.bucket.name)
            return True
        except S3Error as e:
            _logger.error(
                "S3: delete Was not able to delete bucket %s to S3 (%s)",
                self.bucket.name,
                e.message,
                exc_info=e,
            )
        return False

    def create_bucket_if_not_exist(self) -> bool:
        """
        Retourne Vrai **si et uniquement si** le bucket à été créé
        Faut si le bucket existait deja ou si il ya eu une erreur
        :return: Vrai si la création à reussi
        """
        try:
            s3_session = self.conn.s3_session
        except Exception as e:
            _logger.error(
                "S3: create_bucket_if_not_exist Was not able to connect to S3 (%s)",
                exc_info=e,
            )
            return False
        try:
            if not self.bucket_exist():
                s3_session.make_bucket(self.bucket.name)
                _logger.info("S3: bucket [%s] created successfully", self.bucket.name)
                return True
        except S3Error as e:
            _logger.error(
                "S3: create_bucket_if_not_exist Was not able to create bucket %s to S3 (%s)",
                self.bucket.name,
                self.conn.host,
                exc_info=e,
            )
            return False
        return False

    def file_exist(self, fname: str, first_dir: str | None = None) -> bool:
        """
        Test l'existance du de l'objet avec le nom `fname`
        :param fname: non de l'object dont il faut tester l'existence
        :param first_dir: un dossier parent au fname si besoin
        :return: Vrai si l'object avec le fname existe
        """
        try:
            s3_session = self.conn.s3_session
        except Exception as e:
            _logger.error("S3: _file_read Was not able to connect to S3 (%s)", exc_info=e)
            return b""

        key = self.bucket.get_key(first_dir, fname)
        bucket_name = self.bucket.name
        try:
            s3_session.stat_object(bucket_name, key)
            return True
        except S3Error:
            return False
        except Exception as e:
            _logger.error("S3: _file_read was not able to read from S3 (%s): %s", key, exc_info=e)
            raise e

    def file_read(self, fname: str, first_dir: str = None) -> bytes:
        """
        Lit l'objet avec le nom `fname`
        `first_dir` sert si besoin à preciser un dossier parent
        :param fname: le nom du fichier, peut contenir une arborecence
        :param first_dir: le nom d'un dossier parent
        :return: une valeur binaire
        """
        try:
            s3_session = self.conn.s3_session
        except Exception as e:
            _logger.error("S3: _file_read Was not able to connect to S3 (%s)", e)
            return b""

        s3_key = None
        bucket_name = self.bucket.name
        key = self.bucket.get_key(first_dir, fname)
        try:
            s3_key = s3_session.get_object(bucket_name, key)
            res = s3_key.data
            _logger.debug("S3: _file_read read %s:%s from bucket successfully", bucket_name, key)
        except S3Error as e:
            _logger.debug(
                "S3: S3Error _file_read was not able to read from S3 (%s): %s",
                key,
                exc_info=e,
            )
            return b""
        except Exception as e:
            _logger.error("S3: _file_read was not able to read from S3 (%s): %s", key, exc_info=e)
            raise e
        finally:
            if s3_key:
                s3_key.close()
                s3_key.release_conn()
        return res

    def file_write(self, fname: str, value: bytes, first_dir: str = None) -> str:
        """
        Ecrit la valeur (`value`) dans le S3 sous le nom `fname`
        `first_dir` permet de préciser un sous dossier si necessaire
        :param fname: nom du fichier, peut contenir l'arboressence complete (Ex: my-dir/file.txt)
        :param value: la valeur binaire
        :param first_dir: un dossier parent au fname
        :return: fname
        """
        try:
            s3_session = self.conn.s3_session
        except S3Error as e:
            _logger.error("S3: _file_write was not able to connect (%s)", e)
            return fname

        bucket_name = self.bucket.name
        key = self.get_key(first_dir, fname)
        try:
            res = s3_session.put_object(bucket_name, key, BytesIO(value), len(value))
            _logger.debug(
                "S3: _file_write %s:%s was successfully uploaded => %s",
                bucket_name,
                key,
                res,
            )
        except S3Error as e:
            _logger.error("S3: _file_write was not able to write (%s): %s", key, e)
            raise e
        # Returning the file name
        return fname

    def mark_for_gc(self, fname: str) -> str | None:
        """
        Met un fichier vide (valeur de 0bytes) dans un sous dossier "checklist" avec le nom fournit en paramettre
        :param fname: le nom du fichier
        :return: fname
        """
        return self.file_write(fname, b"", "checklist")

    def file_delete(self, fname: str) -> bool:
        """
        Supprime le fichier ayant le `fname` et retourne Vrai si il n'y a pas d'erreur
        :param fname: le nom du fichier à supprimer
        :return: Vrai si la suppression ne leve pa d'erreur
        """
        try:
            s3_session = self.conn.s3_session
        except Exception as e:
            _logger.error("S3: file_delete was not able to connect (%s)", e)
            return False
        bucket_name = self.bucket.name
        key = self.bucket.get_key(fname)
        try:
            s3_session.stat_object(bucket_name, key)
            try:
                s3_session.remove_object(bucket_name, key)
                _logger.debug("S3: _file_delete deleted %s:%s successfully", bucket_name, key)
            except Exception as e:
                _logger.error(
                    "S3: _file_delete was not able to gc (%s:%s) : %s",
                    bucket_name,
                    key,
                    e,
                )
                return False
        except Exception as e:
            _logger.error(
                "S3: _file_delete get_stat was not able to gc (%s:%s) : %s",
                bucket_name,
                key,
                e,
            )
            return False
        return True

    def get_checklist_objects(self) -> dict[str, tuple[str, str]]:
        checklist = {}
        prefix = self.get_key("checklist")
        # retrieve the file names from the checklist
        for s3_key_gc in self.conn.s3_session.list_objects(self.bucket.name, prefix=prefix, recursive=True):
            if not s3_key_gc.is_dir:
                fname = s3_key_gc.object_name[len(prefix + "/") :]
                real_key_name = fname
                if self.bucket.sub_dir_name:
                    real_key_name = f"{self.bucket.sub_dir_name}/{fname}"
                checklist[fname] = (real_key_name, s3_key_gc.object_name)
        return checklist

    def file_delete_multi(self, to_deletes: dict[str, str], whitelist: Iterable[str] = None) -> int:
        whitelist = whitelist or []
        removed = 0
        to_mass_deletes = []

        for real_key_name, check_key_name in to_deletes.values():
            to_mass_deletes.append(DeleteObject(check_key_name))
            if not whitelist or real_key_name not in whitelist:
                to_mass_deletes.append(DeleteObject(self.get_key(real_key_name)))

        try:
            errors = list(self.conn.s3_session.remove_objects(self.bucket.name, to_mass_deletes))
            removed = len(to_mass_deletes) and len(to_mass_deletes) - len(errors) or 0
            _logger.debug("S3: _file_gc_s3 deleted %s:%s successfully", self.bucket.name, removed)
        except Exception as e:
            _logger.error("S3: _file_gc_s3 was not able to gc (%s) : %s", self.bucket.name, e)
        return removed
