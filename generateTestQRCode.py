
import segno
import segno_pil
from PIL import Image, ImageTk, ImageDraw, ImageFont
import uuid
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from monero.seed import Seed
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkcalendar import Calendar
import os

template= """\"Seed\":\"{0}\",
\"CreationDate\":\"{1}\",
\"TXids\":\"{2}\""""

geo ="400x300"
## Generate wallet

root = tk.Tk()

root.configure(background='white')

root.geometry(geo)
default = datetime.today()

cal = Calendar(root, selectmode= 'day',year = default.year,month=default.month,day=default.day)
cal.pack(pady = 20)
root.title("Select current date")

saved = cal.get_date()
def select_date():
	global btn
	saved = cal.get_date()
	root.quit()
	cal.destroy()
	btn.place_forget()
	root.withdraw()
	#root.destroy()

def resize(dim,img):
	wp = (dim / float(img.size[0]))
	hsize = int((float(img.size[1]) * float(wp)))
	img = img.resize((dim,hsize), Image.LANCZOS)
	return img


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def formatData(root,phrase,date,txids):
	global data
	data = ("{" + template.format(phrase,date,txids) +"}").encode()
	root.destroy()
btn = tk.Button(root, text = "Current Date is selected", command=select_date)
btn.place(x=110,y=200)


root.mainloop()

wallet = Seed()

#data = ("{" + template.format(wallet.phrase,wallet.secret_spend_key(),wallet.secret_view_key(),wallet.public_spend_key(),wallet.public_view_key(),wallet.public_address(),str(saved)) + "}").encode()

root.geometry("600x750")

canvas = tk.Canvas(root,bg='white',width=599,height=849)
canvas.pack()
text = tk.Text(root,bg="white")
l = tk.Label(root,text= "test")
text.pack()
l.pack()
canvas.create_text(300, 50, text="Scan QR code in Wallet app to send XMR to giftcard", fill="black", font=('Helvetica 15 bold'))
receive = ImageTk.PhotoImage(resize(580,segno_pil.write_pil(segno.make_qr(b"monero:" + str(wallet.public_address()).encode()))),master=canvas)
canvas.create_text(300,650,text="Enter TX ids of deposit transactions as a comma seperated list")
txInput = tk.Entry(root,width=40)
txInput.config(font=('Helvetica 16'))
canvas.create_window(300,680,window=txInput)
root.title("")
submit = tk.Button(root, text="Submit",width=20,height=1,command=lambda : formatData(root, wallet.phrase,str(saved),txInput.get()))

item = canvas.create_image(299,349,image=receive)

canvas.create_window(300,730,window=submit)
root.deiconify()
canvas.mainloop()

## Encryption Code
key = get_random_bytes(32)

cipher = AES.new(key, AES.MODE_GCM)

ciphertext, tag = cipher.encrypt_and_digest(data)

nonce = cipher.nonce

package = bytearray(nonce)
package.extend(tag)
package.extend(ciphertext)


## Qr Code generation
qr = segno.make_qr(base64.b64encode(package))


#qrpath = './qrcode.eps'
qrpath = "./" + str(uuid.uuid4()) + ".eps"
backup = filedialog.asksaveasfile(title="Location to save backup information for giftcard",mode='w+b',defaultextension=".txt")


[ backup.write(x) for x in (("Recovery information for giftcard wallet created on " + datetime.now().strftime("%B %d %Y") +"\n").encode(),data) ]
backup.close()

qr.save(qrpath,scale=4,border=0)

img = resize(138,Image.open(qrpath))

templatepath = resource_path('./XMR-GiftCard-template.png')



background = Image.open(templatepath)

background.paste(img,(186,3))

draw = ImageDraw.Draw(background)

font = ImageFont.truetype(resource_path('./Arial.ttf'),12)
draw.text((168,158),base64.b64encode(key).decode('utf-8')[0:21],fill="black",align="left",font=font)
draw.text((168,171),base64.b64encode(key).decode('utf-8')[21:],fill="black",align="left",font=font)
indexcard = filedialog.asksaveasfile(title="Location to save generated giftcard", defaultextension=".pdf",mode='w+b')
background.save(indexcard)

os.remove(qrpath)

#print(base64.b64encode(key).decode('utf-8'))
#print(base64.b64encode(nonce).decode())
#print(base64.b64encode(tag).decode())

#root =tk.Tk()



background.show()
