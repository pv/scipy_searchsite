import os
import re
import tempfile
import urllib
import shutil
import zipfile
import tarfile

from whoosh import index
from whoosh.qparser import QueryParser

from django.db import models
from django.conf import settings

class SearchIndex(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, help_text="Name to display")
    url = models.CharField(max_length=4096, null=True,
                           help_text="URL for a downloadable .zip file")

    # --

    @property
    def _dirname(self):
        """
        Index directory name
        """
        return os.path.join(settings.SCIPY_SEARCH_INDICES, '%d' % self.id)

    def _get_index(self):
        """
        Get (cached) a Whoosh indexer object for this index. 
        """
        key = '_index_%d' % self.id
        cls = SearchIndex
        if not hasattr(cls, key):
            setattr(cls, key, index.open_dir(self._dirname))
        return getattr(cls, key)

    def _close_index(self):
        """
        Close any open cached indices associated 
        """
        key = '_index_%d' % self.id
        cls = SearchIndex
        ix = getattr(cls, key, None)
        if ix is not None:
            ix.close()
            delattr(cls, key)

    # --

    def search(self, query, limit=100):
        """Perform a search in the Whoosh query language"""
        ix = self._get_index()
        qp = QueryParser("body", schema=ix.schema)
        q = qp.parse(query)
        s = ix.searcher()
        return [dict(url='%s/%s.html' % (self.url, hit['name']),
                     title=hit.get('title', u'No title'))
                for hit in s.search(q, limit=limit)]

    # -- 

    @property
    def updateable(self):
        return '://' in self.url

    def update(self):
        """
        Update this index by downloading it from the Internet.
        """
        if not self.updateable:
            return False

        index_url = self.url + '/' + 'whoosh-index.zip'

        tmp_file = tempfile.TemporaryFile()
        try:
            try:
                f = urllib.urlopen(index_url)
                copyfileobj(f, tmp_file)
                tmp_file.seek(0)
            except IOError, e:
                return False
        finally:
            f.close()

        if os.path.isdir(self._dirname):
            shutil.rmtree(self._dirname)
        os.makedirs(self._dirname)

        VALID_EXTENSIONS = ('dci', 'dcz', 'pst', 'tiz', 'toc')

        try:
            container = zipfile.ZipFile(tmp_file)
            members = [x for x in container.namelist()
                       if x.split('.')[-1] in VALID_EXTENSIONS]
            container.extractall(path=self._dirname, members=members)
        except IOError:
            return False

        return True
