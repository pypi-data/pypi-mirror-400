# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-01-04 21:48
# @Author : 毛鹏

import json as json_lib
from urllib.parse import urlencode

from PySide6.QtCore import QUrl, QObject, Signal, Slot, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class HttpRequest(QObject):
    request_finished = Signal(str)

    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.on_finished)

    def _prepare_request(self, url, headers=None, params=None):
        if params:
            url += "?" + urlencode(params)
        request = QNetworkRequest(QUrl(url))
        if headers:
            for key, value in headers.items():
                request.setRawHeader(key.encode('utf-8'), value.encode('utf-8'))
        return request

    def _prepare_body(self, data=None, json=None):
        if json:
            body = QByteArray(json_lib.dumps(json).encode('utf-8'))
            content_type = "application/json"
        elif data:
            body = QByteArray(urlencode(data).encode('utf-8'))
            content_type = "application/x-www-form-urlencoded"
        else:
            body = QByteArray()
            content_type = None

        return body, content_type

    def get(self, url, headers=None, params=None):
        request = self._prepare_request(url, headers, params)
        self.manager.get(request)

    def post(self, url, headers=None, params=None, data=None, json=None):
        request = self._prepare_request(url, headers, params)
        body, content_type = self._prepare_body(data, json)
        if content_type:
            request.setHeader(QNetworkRequest.ContentTypeHeader, content_type)  # type: ignore
        self.manager.post(request, body)

    def put(self, url, headers=None, params=None, data=None, json=None):
        request = self._prepare_request(url, headers, params)
        body, content_type = self._prepare_body(data, json)
        if content_type:
            request.setHeader(QNetworkRequest.ContentTypeHeader, content_type)  # type: ignore
        self.manager.put(request, body)

    def delete(self, url, headers=None, params=None):
        request = self._prepare_request(url, headers, params)
        self.manager.deleteResource(request)

    @Slot(QNetworkReply)
    def on_finished(self, reply):
        if reply.error() == QNetworkReply.NoError:  # type: ignore
            data = reply.readAll().data().decode('utf-8')
            self.request_finished.emit(data)
        else:
            self.request_finished.emit(f"Error: {reply.errorString()}")
        reply.deleteLater()
