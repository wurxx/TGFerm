from fastapi import *
import uvicorn
import sqlite3
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def inlive(app:FastAPI):
    yield


class StorageBase():
    def __init__(self):
        self.conn = sqlite3.connect('base.db')
        self.cur = self.conn.cursor()
    
    async def addAcc(self, phone, api_id, api_hash, twoFa, proxy, online):
        try:
            self.cur.execute("INSERT INTO accs VALUES (?, ?, ?, ?, ?, ?)", (phone, api_id, api_hash, twoFa, proxy, online))
            self.conn.commit()
            return True
        except Exception as e:print(e);return e
    async def getAccs(self):
        try:return self.cur.execute("SELECT * FROM accs").fetchall()
        except Exception as e:print(e);return e
    async def newProxB(self, phone, proxy):
        try:
            self.cur.execute("UPDATE accs SET proxy = ? WHERE phone = ?", (proxy, phone))
            self.conn.commit()
            return True
        except Exception as e:print(e);return e
    async def newOnlineB(self, phone, online):
        try:
            self.cur.execute("UPDATE accs SET online = ? WHERE phone = ?", (online, phone))
            self.conn.commit()
            return True
        except Exception as e:print(e);return e
    async def delAcc(self, acc):
        try: 
            self.cur.execute('DELETE FROM accs WHERE phone = ?', (acc,))
            self.conn.commit()
            return True
        except Exception as e:return e
    
    async def addAdmin(self, adminId):
        try:
            self.cur.execute('INSERT INTO admins VALUES (?)', (adminId,))
            self.conn.commit()
            return True
        except Exception as e:return e
    async def delAdmin(self, adminId):
        try:
            self.cur.execute('DELETE FROM admins WHERE id = ?', (adminId,))
            self.conn.commit()
            return True
        except Exception as e:return e
    async def getAdmins(self):
        try:
            return [x[0] for x in self.cur.execute("SELECT * FROM admins").fetchall()]
        except Exception as e:return e

app = FastAPI(lifespan=inlive)
base = StorageBase()
    
@app.post("/addTg")
async def addingtg(phone, api_id, api_hash, twoFa=None, proxy=None, online=None):
    if proxy.lower() == 'none':proxy=None
    if twoFa.lower() == 'none':twoFa=None
    return await base.addAcc(phone, api_id, api_hash, twoFa, proxy, online)

@app.post("/delAcc")
async def delletingc(acc):return await base.delAcc(acc)


@app.get("/accs")
async def getaccs():return await base.getAccs()

@app.post("/updateProxy")
async def newproxx(phone, proxy):return await base.newProxB(phone, proxy)
    
@app.post("/updateOnline")
async def updonlinee(phone, online=None):
    if online == 'None':online=None
    return await base.newOnlineB(phone, online)

@app.post('/addAdmin')
async def addadminn(id): return await base.addAdmin(id)

@app.post('/delAdmin')
async def addadminn(id): return await base.delAdmin(id)

@app.get('/admins')
async def getsaddmin():return await base.getAdmins()
    
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8855, reload=True)