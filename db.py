#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import datetime
import time

def getRss():
    conn = sqlite3.connect('rss/rss.db3')
    cur = conn.cursor()

    query_sql = '''
    SELECT title, xml_url FROM t_rss WHERE status = 1 ORDER BY RANDOM() limit 200
    '''

    cur.execute(query_sql)

    list = []

    for title, xml_url in cur.fetchall():
        list.append(xml_url)

    # print(list)

    cur.close()
    conn.close()

    return list

def updateRssInvalid(url):
    conn = sqlite3.connect('rss/rss.db3')
    cur = conn.cursor()

    sql = '''
    update t_rss set status = 2, updated_at = ? where xml_url in (?)
    '''

    cur.execute(sql, [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), url])
    conn.commit()

    cur.close()
    conn.close()

def toDate(d):
    if d:
        return datetime.datetime(d[0], d[1], d[2], d[3], d[4], d[5])
    return datetime.datetime.now()

def addArticles(list):
    conn = sqlite3.connect('rss/rss.db3')
    cur = conn.cursor()

    for (ret, feed, link, articles) in list:
        try:
            for item in articles:
                cur.execute('''
                insert into t_article(feed_name, feed_url, title, url, status, created_at, published_at)
                values(?, ?, ?, ?, ?, ?, ?)
                ''', [
                    feed,
                    link,
                    item.title,
                    item.link,
                    0,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    toDate(item.published_parsed)
                    ])

            cur.execute('''
            update t_rss set article_num = (select count(*) from t_article b where b.feed_url = ?), updated_at = ?
            where xml_url = ?
            ''', [
                link,
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                link
                ])
        except Exception as e:
            print(str(e))

    conn.commit()

    cur.close()
    conn.close()


def getArticles():
    conn = sqlite3.connect('rss/rss.db3')
    cur = conn.cursor()


    fromDate = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    toDate = datetime.datetime.combine(datetime.datetime.now() + datetime.timedelta(days=1), datetime.time.min)

    cur.execute('''
    select feed_name, feed_url, title, url from t_article where published_at >= ? and published_at < ? order by feed_name
    ''', [
        fromDate.strftime('%Y-%m-%d'),
        toDate.strftime('%Y-%m-%d')
        ])

    result = cur.fetchall()

    cur.close()
    conn.close()
    return result

def getArticlesForReadme():
    conn = sqlite3.connect('rss/rss.db3')
    cur = conn.cursor()


    # fromDate = datetime.datetime.combine(datetime.datetime.now() + datetime.timedelta(hours=-8), datetime.time.min)
    fromDate = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    toDate = datetime.datetime.combine(datetime.datetime.now() + datetime.timedelta(days=1), datetime.time.min)

    cur.execute('''
    select feed_name, feed_url, title, url, published_at from t_article where published_at >= ? and published_at < ? order by updated_at desc
    ''', [
        fromDate.strftime('%Y-%m-%d'),
        toDate.strftime('%Y-%m-%d')
        ])

    result = cur.fetchall()

    cur.close()
    conn.close()
    return result

def getArticlesForBot():
    conn = sqlite3.connect('rss/rss.db3')
    cur = conn.cursor()

    cur.execute('''
    select id, feed_name, feed_url, title, url from t_article where status = 0 order by updated_at desc limit 20
    ''')

    result = cur.fetchall()

    cur.close()
    conn.close()
    return result

def updateArticlesStatus(ids: list):
    conn = sqlite3.connect('rss/rss.db3')
    cur = conn.cursor()

    for id in ids:
        cur.execute('''
        update t_article set status = 1 where id = ?
        ''', [id])

    conn.commit()

    cur.close()
    conn.close()
