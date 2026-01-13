#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import collections.abc
import logging
import os
import smtplib
import warnings
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from airflow.configuration import conf
from airflow.exceptions import AirflowConfigException, AirflowException

log = logging.getLogger(__name__)


def send_email(
    to: Union[List[str], Iterable[str]],
    subject: str,
    html_content: str,
    files: Optional[List[str]] = None,
    dryrun: bool = False,
    cc: Optional[Union[str, Iterable[str]]] = None,
    bcc: Optional[Union[str, Iterable[str]]] = None,
    mime_subtype: str = 'mixed',
    mime_charset: str = 'utf-8',
    conn_id: Optional[str] = None,
    **kwargs,
):
    """Send email using backend specified in EMAIL_BACKEND."""
    backend = conf.getimport('email', 'EMAIL_BACKEND')
    backend_conn_id = conn_id or conf.get("email", "EMAIL_CONN_ID")
    to_list = get_email_address_list(to)
    to_comma_separated = ", ".join(to_list)

    return backend(
        to_comma_separated,
        subject,
        html_content,
        files=files,
        dryrun=dryrun,
        cc=cc,
        bcc=bcc,
        mime_subtype=mime_subtype,
        mime_charset=mime_charset,
        conn_id=backend_conn_id,
        **kwargs,
    )


def send_email_smtp(
    to: Union[str, Iterable[str]],
    subject: str,
    html_content: str,
    files: Optional[List[str]] = None,
    dryrun: bool = False,
    cc: Optional[Union[str, Iterable[str]]] = None,
    bcc: Optional[Union[str, Iterable[str]]] = None,
    mime_subtype: str = 'mixed',
    mime_charset: str = 'utf-8',
    conn_id: str = "smtp_default",
    **kwargs,
):
    """
    Send an email with html content

    >>> send_email('test@example.com', 'foo', '<b>Foo</b> bar', ['/dev/null'], dryrun=True)
    """
    smtp_mail_from = conf.get('smtp', 'SMTP_MAIL_FROM')

    msg, recipients = build_mime_message(
        mail_from=smtp_mail_from,
        to=to,
        subject=subject,
        html_content=html_content,
        files=files,
        cc=cc,
        bcc=bcc,
        mime_subtype=mime_subtype,
        mime_charset=mime_charset,
    )

    send_mime_email(e_from=smtp_mail_from, e_to=recipients, mime_msg=msg, conn_id=conn_id, dryrun=dryrun)


def build_mime_message(
    mail_from: str,
    to: Union[str, Iterable[str]],
    subject: str,
    html_content: str,
    files: Optional[List[str]] = None,
    cc: Optional[Union[str, Iterable[str]]] = None,
    bcc: Optional[Union[str, Iterable[str]]] = None,
    mime_subtype: str = 'mixed',
    mime_charset: str = 'utf-8',
    custom_headers: Optional[Dict[str, Any]] = None,
) -> Tuple[MIMEMultipart, List[str]]:
    """
    Build a MIME message that can be used to send an email and
    returns full list of recipients.

    :param mail_from: Email address to set as email's from
    :param to: List of email addresses to set as email's to
    :param subject: Email's subject
    :param html_content: Content of email in HTML format
    :param files: List of paths of files to be attached
    :param cc: List of email addresses to set as email's CC
    :param bcc: List of email addresses to set as email's BCC
    :param mime_subtype: Can be used to specify the subtype of the message. Default = mixed
    :param mime_charset: Email's charset. Default = UTF-8.
    :param custom_headers: Additional headers to add to the MIME message.
        No validations are run on these values and they should be able to be encoded.
    :return: Email as MIMEMultipart and list of recipients' addresses.
    """
    to = get_email_address_list(to)

    msg = MIMEMultipart(mime_subtype)
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = ", ".join(to)
    recipients = to
    if cc:
        cc = get_email_address_list(cc)
        msg['CC'] = ", ".join(cc)
        recipients = recipients + cc

    if bcc:
        # don't add bcc in header
        bcc = get_email_address_list(bcc)
        recipients = recipients + bcc

    msg['Date'] = formatdate(localtime=True)
    mime_text = MIMEText(html_content, 'html', mime_charset)
    msg.attach(mime_text)

    for fname in files or []:
        basename = os.path.basename(fname)
        with open(fname, "rb") as file:
            part = MIMEApplication(file.read(), Name=basename)
            part['Content-Disposition'] = f'attachment; filename="{basename}"'
            part['Content-ID'] = f'<{basename}>'
            msg.attach(part)

    if custom_headers:
        for header_key, header_value in custom_headers.items():
            msg[header_key] = header_value

    return msg, recipients


def send_mime_email(
    e_from: str, e_to: List[str], mime_msg: MIMEMultipart, conn_id: str = "smtp_default", dryrun: bool = False
) -> None:
    """Send MIME email."""
    smtp_host = conf.get('smtp', 'SMTP_HOST')
    smtp_port = conf.getint('smtp', 'SMTP_PORT')
    smtp_starttls = conf.getboolean('smtp', 'SMTP_STARTTLS')
    smtp_ssl = conf.getboolean('smtp', 'SMTP_SSL')
    smtp_retry_limit = conf.getint('smtp', 'SMTP_RETRY_LIMIT')
    smtp_timeout = conf.getint('smtp', 'SMTP_TIMEOUT')
    smtp_user, smtp_password = None, None
    if conn_id is not None:
        try:
            from airflow.hooks.base import BaseHook

            conn = BaseHook.get_connection(conn_id)
            smtp_user = conn.login
            smtp_password = conn.password
        except AirflowException:
            pass
    if smtp_user is None or smtp_password is None:
        # warnings.warn(
        #     "Fetching SMTP credentials from configuration variables will be deprecated in a future "
        #     "release. Please set credentials using a connection instead.",
        #     PendingDeprecationWarning,
        #     stacklevel=2,
        # )
        try:
            smtp_user = conf.get('smtp', 'SMTP_USER')
            smtp_password = conf.get('smtp', 'SMTP_PASSWORD')
        except AirflowConfigException:
            log.debug("No user/password found for SMTP, so logging in with no authentication.")

    if not dryrun:
        for attempt in range(1, smtp_retry_limit + 1):
            log.info("Email alerting: attempt %s", str(attempt))
            try:
                conn = _get_smtp_connection(smtp_host, smtp_port, smtp_timeout, smtp_ssl)
            except smtplib.SMTPServerDisconnected:
                if attempt < smtp_retry_limit:
                    continue
                raise

            if smtp_starttls:
                conn.starttls()
            if smtp_user and smtp_password:
                conn.login(smtp_user, smtp_password)
            log.info("Sent an alert email to %s", e_to)
            conn.sendmail(e_from, e_to, mime_msg.as_string())
            conn.quit()
            break


def get_email_address_list(addresses: Union[str, Iterable[str]]) -> List[str]:
    """Get list of email addresses."""
    if isinstance(addresses, str):
        return _get_email_list_from_str(addresses)

    elif isinstance(addresses, collections.abc.Iterable):
        if not all(isinstance(item, str) for item in addresses):
            raise TypeError("The items in your iterable must be strings.")
        return list(addresses)

    received_type = type(addresses).__name__
    raise TypeError(f"Unexpected argument type: Received '{received_type}'.")


def _get_smtp_connection(host: str, port: int, timeout: int, with_ssl: bool) -> smtplib.SMTP:
    return (
        smtplib.SMTP_SSL(host=host, port=port, timeout=timeout)
        if with_ssl
        else smtplib.SMTP(host=host, port=port, timeout=timeout)
    )


def _get_email_list_from_str(addresses: str) -> List[str]:
    delimiters = [",", ";"]
    for delimiter in delimiters:
        if delimiter in addresses:
            return [address.strip() for address in addresses.split(delimiter)]
    return [addresses]


# 转化list 为 一条文本消息
def list_to_string(title, content, head=None, min_space=0):  # 标题，内容，首行，字符串最小长度
    # 将首行加入内容
    if head is not None:
        content_list = [head]
        for list in content:
            content_list.append(list)
        max_Len_Array = [len(word) for word in head]
        max_column = len(head)
    else:
        content_list = content
        max_Len_Array = [min_space for x in range(len(content[0]))]  # 创建一个列表
        max_column = len(content[0])
    # 寻找每一列的长度最大值
    for line in content_list:
        index = -1
        line = [str(word).replace('None', '0') for word in line[:max_column]]
        for word in line:
            index += 1
            if max_Len_Array[index] < len(word):
                max_Len_Array[index] = len(word)
    msg = title + '\n' + int(sum(max_Len_Array) + len(max_Len_Array)) * '-' + '\n'  #
    # 有序构造msg
    for line in content_list:
        line = [str(word).replace('None', '0') for word in line[:max_column]]
        index = -1
        for word in line:
            index += 1
            msg = msg + word + chr(12288) + int(
                max_Len_Array[index] - len(word.encode('gbk'))) * " " + chr(12288)
        msg = msg + '\n'
    return msg.upper()  # 返回大写string


# 输入标题, 数据清单,表头
def list_to_html(title, content_list, head=None):
    msg = ''
    msg = msg + '<table border="1" cellspacing="0" text-align:center style="border-collapse:collapse;">'
    # 表头
    if head is not None:
        for word in head:
            msg = msg + '<th>' + word + '</th>'
        msg = msg + '</tr>'
        max_column = len(head)
    else:
        max_column = len(content_list[0])
    # 对表格内容构建html
    for row in content_list:
        msg = msg + '<tr>'
        for word in row[:max_column]:
            msg = msg + '<td style="font-size:14px">' + str(word) + '</td>'
        msg = msg + '</tr>'
    msg = msg + '</table>'
    htmls = """
            <font color="blue">%s</font>
            <style>.alsp{ font-family:"楷体"; font-size:18px;}</style>
            <font class="alsp">
            %s
            </font>
            """ % (title, msg)
    return htmls


# 构建完整的html
def construct_html(html):
    htmls = """
        <html>
            <body>
            %s
            </body>
        </html>
            """ % (html)
    return htmls


def send_list_mail(sub, title, content_list, head=None, to_list=None,
                   flag='plain'):  # 邮件标题，列表标题，列表内容[[]]，列表首行[]，收件人string，邮件类型文本
    if flag == 'plain':
        msg = list_to_string(title, content_list, head)
    else:
        msg = construct_html(list_to_html(title, content_list, head))
    send_email(to=to_list, subject=sub, html_content=msg)


def fun_email(sub, content, to_list=None):  # 邮件标题，文本，收件人，邮件类型文本
    if not to_list:
        to_list = conf.get("smartpip", "email_list")
        if not to_list:
            return
    send_email(to=to_list, subject=sub, html_content=content)


def list_email(sub, title, contents, head=None, to_list=None, flag='html'):
    if not to_list:
        to_list = conf.get("smartpip", "email_list")
        if not to_list:
            return
    send_list_mail(sub, title, contents, head, to_list, flag)
