from fsspec.spec import AbstractBufferedFile


class AlluxioBasedFile(AbstractBufferedFile):
    def __init__(self, alluxio, path, mode="rb", **kwargs):
        super().__init__(alluxio, path, mode, **kwargs)
        if alluxio and alluxio.logger:
            self.logger = alluxio.logger

    def seek(self, offset, whence=0):
        try:
            return super().seek(offset, whence)
        except Exception as e:
            self.logger.error(f"Seek failed: {e}")
            raise e

    def close(self, *args, **kwargs):
        try:
            return super().close(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Close failed: {e}")
            raise e

    def commit(self, *args, **kwargs):
        try:
            return super().commit(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Commit failed: {e}")
            raise e

    def discard(self, *args, **kwargs):
        try:
            return super().discard(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Discard failed: {e}")
            raise e

    def flush(self, *args, **kwargs):
        try:
            return super().flush(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Flush failed: {e}")
            raise e

    def info(self, *args, **kwargs):
        try:
            return super().info(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Info failed: {e}")
            raise e

    def isatty(self, *args, **kwargs):
        try:
            return super().isatty(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Isatty failed: {e}")
            raise e

    def read(self, *args, **kwargs):
        try:
            return super().read(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Read failed: {e}")
            raise e

    def readable(self, *args, **kwargs):
        try:
            return super().readable(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Readable failed: {e}")
            raise e

    def readinto(self, *args, **kwargs):
        try:
            return super().readinto(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Readinto failed: {e}")
            raise e

    def readinto1(self, *args, **kwargs):
        try:
            return super().readinto1(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Readinto1 failed: {e}")
            raise e

    def readline(self, *args, **kwargs):
        try:
            return super().readline(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Readline failed: {e}")
            raise e

    def readlines(self, *args, **kwargs):
        try:
            return super().readlines(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Readlines failed: {e}")
            raise e

    def readuntil(self, *args, **kwargs):
        try:
            return super().readuntil(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Readuntil failed: {e}")
            raise e

    def seekable(self, *args, **kwargs):
        try:
            return super().seekable(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Seekable failed: {e}")
            raise e

    def tell(self, *args, **kwargs):
        try:
            return super().tell(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Tell failed: {e}")
            raise e

    def truncate(self, *args, **kwargs):
        try:
            return super().truncate(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Truncate failed: {e}")
            raise e

    def writable(self, *args, **kwargs):
        try:
            return super().writable(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Writable failed: {e}")
            raise e

    def write(self, *args, **kwargs):
        try:
            return super().write(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Write failed: {e}")
            raise e

    def writelines(self, *args, **kwargs):
        try:
            return super().writelines(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Writelines failed: {e}")
            raise e
