import re
import sqlite3
import tweepy
import datetime
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def getTweet():
    consumer_key = "#################################################"
    consumer_secret = "#################################################"
    access_token = '"#################################################"'
    access_token_secret = "#################################################"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    tgl = datetime.date.today()
    twodays = datetime.timedelta(days=5)
    rangetgl = tgl - twodays

    search_words = 'vaksin covid'
    new_search = search_words + " -filter:retweets"
    tweets = tweepy.Cursor(api.search, q=new_search,
                           lang="id", since=rangetgl).items(5000)

    items = []
    for tweet in tweets:
        item = []
        item.append(tweet.id)
        item.append(tweet.user.screen_name)
        item.append(tweet.created_at)
        item.append(' '.join(re.sub(
            "(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet.text).split()))
        items.append(item)
    # hasil = pd.DataFrame(data=items, columns=['User', 'Tanggal', 'Tweet'])
    # hasil.to_csv('dataTwitter.csv', index=False)
    # print(hasil)

    connection = sqlite3.connect('Teguh_Setiawan.db')
    for item in items:
        querry = '''INSERT OR IGNORE INTO userTwitter (idTweet,username,tanggal,tweet) VALUES (?,?,?,?);'''
        cursor = connection.cursor()
        cursor.execute(querry, item)
    connection.commit()
    print('Berhasil')
    cursor.close()
    connection.close()


def updateSentimen():

    connection = sqlite3.connect("Teguh_Setiawan.db")
    cur = connection.cursor()
    crud_query = '''select idTweet,tweet from userTwitter'''

    cursor = connection.cursor()
    cursor.execute(crud_query)
    hasilsemua = cursor.fetchall()

    pos_list = open("./kata_positif.txt", "r")
    pos_kata = pos_list.readlines()
    neg_list = open("./kata_negatif.txt", "r")
    neg_kata = neg_list.readlines()

    sentimen = []
    for item in hasilsemua:
        count_p = 0
        count_n = 0
        for kata_pos in pos_kata:
            if kata_pos.strip() in item[1]:
                count_p += 1
        for kata_neg in neg_kata:
            if kata_neg.strip() in item[1]:
                count_n += 1
        # print("positif: "+str(count_p))
        # print("negatif: "+str(count_n))
        sentimen.append(count_p - count_n)
        sentimen.append(item[0])

    def OnetoMulti(l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]

    Nsen = OnetoMulti(sentimen, 2)
    # print(Nsen)

    for sen in Nsen:
        queryInput = '''update userTwitter set sentimen=? where idTweet=?'''
        cursor = connection.cursor()
        cursor.execute(queryInput, (sen))
    connection.commit()
    print('Berhasil')
    cursor.close()
    connection.close()


def lihatData(input1, input2):
    connection = sqlite3.connect("Teguh_Setiawan.db")
    cur = connection.cursor()
    query = '''SELECT username,tanggal,tweet FROM userTwitter WHERE tanggal BETWEEN ? AND ? '''
    cur.execute(query, (input1, input2))
    hasil = cur.fetchall()

    # for data in hasil:
    #     print(data)

    print('Terdapat Sebanyak :', len(hasil), 'Tweet')


def visualitation(input1, input2):
    connection = sqlite3.connect("Teguh_Setiawan.db")
    cur = connection.cursor()
    query = '''SELECT tanggal,tweet FROM userTwitter WHERE tanggal BETWEEN ? AND ? '''
    cur.execute(query, (input1, input2))
    hasil = cur.fetchall()

    pos_list = open("./kata_positif.txt", "r")
    pos_kata = pos_list.readlines()
    neg_list = open("./kata_negatif.txt", "r")
    neg_kata = neg_list.readlines()

    sentimen = []
    for item in hasil:
        count_p = 0
        count_n = 0
        for kata_pos in pos_kata:
            if kata_pos.strip() in item[1]:
                count_p += 1
        for kata_neg in neg_kata:
            if kata_neg.strip() in item[1]:
                count_n += 1
        # print("positif: "+str(count_p))
        # print("negatif: "+str(count_n))
        sentimen.append(count_p - count_n)
        # sentimen.append(item[0])

    print("Nilai Rata-Rata: "+str(np.mean(sentimen)))
    print("Nilai Median: "+str(np.median(sentimen)))
    print("Standar deviasi: "+str(np.std(sentimen)))

    labels, counts = np.unique(sentimen, return_counts=True)
    plt.bar(labels, counts, align='center')
    plt.gca().set_xticks(labels)
    # plt.title(words)
    plt.show()


while True:
    print('='*100)
    print('Apa yang ingin anda lakukan ?')
    print('1. Update Data \n2. Update Nilai sentimen \n3. Lihat Data \n4. Visualisasi \n5. Keluar')
    try:
        operasi = int(input('Inputan Anda : '))
        if operasi == 1:
            getTweet()
        elif operasi == 2:
            updateSentimen()
        elif operasi == 3:
            input1 = input('Masukan Tanggal awal (format : 2020-04-24)')
            input2 = input('Masukan Tanggal akhir (format : 2020-04-24)')
            lihatData(input1, input2)
        elif operasi == 4:
            input1 = input('Masukan Tanggal awal (format : 2020-04-24)')
            input2 = input('Masukan Tanggal akhir (format : 2020-04-24)')
            visualitation(input1, input2)
        elif operasi == 5:
            print('Anda keluar dari sistem  ')
            break
        else:
            print('Inputan anda melebihi Menu')
            break
    except ValueError:
        print('Input yang anda masukan bukan Integer')
