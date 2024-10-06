import mysql.connector
import streamlit as st
import time
from datetime import datetime
import pandas as pd


db = mysql.connector.connect(
    host = st.secrets.mysql.host,
    user = st.secrets.mysql.user ,
    password = st.secrets.mysql.password,
    database = st.secrets.mysql.database
)               

dt = datetime.now()
timestamp = datetime.timestamp(dt)
date_time = datetime.fromtimestamp(timestamp)
ts = date_time.strftime("%d-%m-%Y %H:%M:%S")

def lihat_stock():
    st.title(":blue[DATA GUDANG WARUNG GAWON]")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sembako")
    liat = cursor.fetchall()

    df = pd.DataFrame(liat, columns=("Id","Kode barang","Nama Barang","Harga","Stock","Terjual"))

    st.dataframe(df, use_container_width=True) 
    
    cursor.execute("SELECT nama_barang FROM sembako")
    intip = cursor.fetchall()
    daftar_barang = [row[0] for row in intip]
    
    pilih_barang = st.selectbox("Cari Barang",daftar_barang)
    
    cursor.execute("SELECT * FROM sembako WHERE nama_barang=%s",(pilih_barang,))
    display = cursor.fetchall()
    
    dp = pd.DataFrame(display, columns=("Id","Kode barang","Nama Barang","Harga","Stock","Terjual"))
    st.dataframe(dp, hide_index=True,use_container_width=True )
    
    kiri,tengah,kanan = st.columns(3)
    
    @st.dialog("Update stock barang")
    def update_stock():
        cursor = db.cursor()
        cursor.execute("SELECT * FROM sembako WHERE nama_barang=%s" , (pilih_barang,))
        stock_awal = cursor.fetchall()
        for x in stock_awal:
            stock_exst = x[4]
        st.dataframe(dp, hide_index=True, use_container_width=True) 
        stock_input = int(st.number_input("Masukan update stock (tambah / kurang) : ",0))
        if st.button("Update"):
            stock = stock_exst + stock_input
            sql = "UPDATE sembako SET stock=%s WHERE nama_barang=%s"
            val = (stock, pilih_barang)
            cursor.execute(sql,val)
            db.commit()
            st.success("Stock barang berhasil di update")
            time.sleep(0.3)
            st.rerun()
        
    if kiri.button("Update Stock", use_container_width=True):
        update_stock()
    
    @st.dialog(f"Apakah anda yakin akan menghapus {pilih_barang}?")
    def busek():
        left,right = st.columns(2)
        if left.button("Ya" , use_container_width=True):
            cursor.execute("DELETE FROM sembako WHERE nama_barang=%s" , (pilih_barang,))
            db.commit()
                
            if cursor.rowcount > 0:
                st.success("Data berhasil dihapus")
                time.sleep(0.3)
                st.rerun()
            else :
                st.warning("Galat")
        elif right.button("Tidak", use_container_width=True):
            st.rerun()  
    if tengah.button("Hapus Data", use_container_width=True):
        busek()
    #
    
    @st.dialog("Tambah Barang baru")
    def add():
        st.write("Tambah barang baru")
        kode_barang = st.text_input("Kode barang : ")
        nama_barang = st.text_input("Nama barang : ")
        harga_barang = int(st.number_input("Harga barang : " , 0))
        stock = int(st.number_input("Stock barang : ", 0))
    
        sql = "INSERT INTO sembako (kode_barang, nama_barang, harga_barang, stock) VALUES (%s,%s,%s,%s)"
        val = (kode_barang.upper(), nama_barang.upper(), harga_barang, stock)
        if st.button("Submit"):
            cursor.execute(sql,val)
            db.commit() 
            if cursor.rowcount > 0:
                st.success(" Berhasil Menambahkan barang")
                time.sleep(0.3)
                st.rerun()
            else :
                st.warning("Data gagal ditambahkan")
                

    if kanan.button("Tambah Barang Baru", use_container_width=True):
        add()


def penjualan():
    cursor = db.cursor()
    
    cursor.execute("SELECT nama_barang FROM sembako")
    intip = cursor.fetchall()
    daftar_barang = [row[0] for row in intip]
    
    pilih_barang = st.selectbox("Cari Barang",daftar_barang)
    
    cursor.execute("SELECT * FROM sembako WHERE nama_barang=%s" , (pilih_barang,)) #cek stock
    cek = cursor.fetchall() 
    for x in cek:
        stock_awal = x[4]
        
    cursor.execute("SELECT * FROM sembako WHERE nama_barang=%s" , (pilih_barang,)) #cek stock
    cek = cursor.fetchall() 
    for x in cek:
        terjual = x[5]
        kdb = x[1]
        harga = x[3]
        
    cursor.execute("SELECT * FROM sembako WHERE nama_barang=%s",(pilih_barang,))
    display = cursor.fetchall()
    
    dp = pd.DataFrame(display, columns=("Id","Kode barang","Nama Barang","Harga","Stock","Terjual"))
    st.dataframe(dp, hide_index=True,use_container_width=True )
        
    qty = int(st.number_input("Qty : ",0))
    penjualan = stock_awal - qty
    update_penjualan = terjual + qty
    totaljual = harga * qty
    
    if st.button("Submit"):
        sql = "UPDATE sembako SET stock=%s WHERE nama_barang=%s"
        val = (penjualan, pilih_barang)
        cursor.execute(sql,val)
        db.commit()
        cursor.execute("UPDATE sembako SET terjual=%s WHERE nama_barang=%s" , (update_penjualan,pilih_barang))
        db.commit()
        sql = "INSERT INTO penjualan (timestamp, kode_barang, nama_barang, harga, qty, total_penjualan) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (ts,kdb,pilih_barang,harga,qty,totaljual)
        cursor.execute(sql,val)
        db.commit()

        if cursor.rowcount > 0:
            st.success("Fungsi penjualan berhasil")
            time.sleep(0.3)
            st.rerun()

def laporan_penjualan():
    st.title(":green[DATA PENJUALAN WARUNG GAWON]")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM penjualan")
    liat = cursor.fetchall()

    df = pd.DataFrame(liat, columns=("Id","Waktu","Kode barang","Nama Barang","Harga","Qty","Total Penjualan"))
    st.dataframe(df, use_container_width=True) 
    

pg = st.navigation([
    st.Page(penjualan, title="Penjualan", icon="🛒"),
    st.Page(lihat_stock, title="Gudang", icon="📦"),
    st.Page(laporan_penjualan, title="laporan Penjualan", icon="📜"),
])

pg.run()

