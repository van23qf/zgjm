#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup

def get_group():
    url = 'https://tools.2345.com/m/zhgjm'
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('请求失败')
    soup = BeautifulSoup(r.content, 'html.parser')
    groups = soup.find_all('a', class_='classify-card-item')
    if not groups:
        raise Exception('没有找到主分类')
    data = []
    for group_ele in groups:
        href = group_ele.get('href')
        if not href:
            continue
        group_id = href.replace('/m/zhgjm/lb/', '').replace('.htm', '')
        if not group_id:
            continue
        group_name = group_ele.get_text().strip()
        if not group_name:
            continue
        data.append({'id': int(group_id), 'name': group_name})
    return data

def get_class(group_id):
    url = 'https://tools-api.2345.com/dream/v1/categoryDream'
    page = 1
    data = []
    while True:
        params = {
            'categoryId': group_id,
            'page': page,
            'pageSize': 40
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            raise Exception('请求失败')
        res = r.json()
        if res['code'] != 200:
            raise Exception('请求失败:'+res['msg'])
        if not res.get('data') or not res['data'].get('list'):
            break
        for item in res['data']['list']:
            data.append({'id': int(item['id']), 'name': item['name']})
        page = page + 1
    return data

def get_detail(class_id):
    url = f'https://tools-api.2345.com/dream/v1/detail?id={class_id}'
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('请求失败')
    res = r.json()
    if res['code'] != 200:
        raise Exception('请求失败:'+res['msg'])
    if not res.get('data') or not res['data'].get('content'):
        raise Exception('没有找到详情')
    return res['data']['content']

def run():
    groups = get_group()
    print(f"共爬取{len(groups)}个分组")
    group_vals = []
    class_vals = []
    detail_vals = []
    for group in groups:
        print(f"爬取分组{group['name']}的分类")
        group_vals.append(f"({group['id']},'{group['name']}')")
        classes = get_class(group['id'])
        print(f"共爬取{len(classes)}个分类")
        print(f"开始爬取详情")
        for class_ in classes:
            class_vals.append(f"({class_['id']},{group['id']},'{class_['name']}')")
            detail = get_detail(class_['id'])
            detail_vals.append(f"({class_['id']},{group['id']},'{detail}')")
    print(f"爬取完成，准备生成sql")
    group_sql = f"INSERT INTO `dream_group` (`gid`, `name`) VALUES {','.join(group_vals)};"
    class_sql = f"INSERT INTO `dream_class` (`cid`, `gid`, `name`) VALUES {','.join(class_vals)};"
    detail_sql = f"INSERT INTO `dream_detail` (`did`, `cid`, `gid`, `detail`) VALUES {','.join(detail_vals)};"
    with open('dream.sql', 'w') as f:
        f.write(group_sql)
        f.write(class_sql)
        f.write(detail_sql)
    print(f"完成！")

if __name__ == '__main__':
    run()
