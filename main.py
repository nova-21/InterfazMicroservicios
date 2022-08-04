import requests
import streamlit as st
from streamlit_tags import st_tags
import json
from bs4 import BeautifulSoup
from lxml import etree

st.set_page_config(layout="wide")
if 'temperatura' not in st.session_state:
    st.session_state['temperatura'] = 20
if 'estadoRiego' not in st.session_state:
    st.session_state['estadoRiego'] = "Apagado"
if 'calefaccion' not in st.session_state:
    st.session_state['calefaccion'] = "OFF"
if 'humedad' not in st.session_state:
    st.session_state['humedad'] = 80
if 'lista_dispositivos' not in st.session_state:
    st.session_state['lista_dispositivos'] = ['Plancha', "Cocina"]
if 'confirmarAgregar' not in st.session_state:
    st.session_state['confirmarAgregar'] = False
if 'iluminacion' not in st.session_state:
    st.session_state['iluminacion'] = {"sala":"","dormitorio":"","cocina":""}
if 'valoresLuz' not in st.session_state:
    st.session_state['valoresLuz'] = {"sala":(0,0),"dormitorio":(0,0),"cocina":(0,0)}
if 'estadoAlerta' not in st.session_state:
    st.session_state['estadoAlerta'] = ""

st.title("Control automático del hogar")

iluminacion,calefaccion,riego,alertas=st.tabs(["Iluminación", "Calefacción", "Riego", "Alertas"])

url = 'http://52.73.98.2:8099/eureka/apps'

document = requests.get(url)

soup= BeautifulSoup(document.content,"lxml-xml")
apps=soup.findAll("hostName")

for app in apps:
    if "calefaccion" in str(app):
        hostCalefaccion=str(app).replace("<hostName>", "").replace("</hostName>", "")
        print(hostCalefaccion)
    if "riego" in str(app):
        hostRiego=str(app).replace("<hostName>", "").replace("</hostName>", "")
        print(hostRiego)
    if "iluminacion" in str(app):
        hostIluminacion=str(app).replace("<hostName>", "").replace("</hostName>", "")
        print(hostIluminacion)
    if "control-aparato" in str(app):
        hostControl = str(app).replace("<hostName>", "").replace("</hostName>", "")
        print(hostControl)

with iluminacion:
    st.subheader("Luces habitaciones")

    estadoLuces=st.empty()

    formLuces = st.form(key="luces")
    with formLuces:
        colHabitaciones,controlLuces=st.columns([1,2])

        with colHabitaciones:
            habitacion=st.radio("Habitación",["Sala","Dormitorio", "Cocina"]).lower()


        with controlLuces:
            lumens = st.slider("Lumens", 0, 25000, key="Cocina",value=10000)
            hora = st.slider("Hora",0,24,key='HCocina')
            y=list(st.session_state['valoresLuz'][habitacion])
            y[0] = lumens
            y[1] = hora
            st.session_state['valoresLuz'][habitacion]=tuple(y)

        if lumens>=0:
            url = 'https://'+hostIluminacion+'/iluminacion/'+habitacion+'/'+str(lumens)+'/'+str(hora)
            x = requests.post(url)
            st.session_state['iluminacion'] = json.loads(x.text)

        st.form_submit_button()

    with estadoLuces:
        sala,cocina,dormitorio=st.columns(3)
        with sala:
            estado = st.session_state['iluminacion']
            st.metric("Sala", st.session_state['iluminacion']["sala"])
        with cocina:
            estado = st.session_state['iluminacion']
            st.metric("Cocina", st.session_state['iluminacion']["cocina"])
        with dormitorio:
            estado = st.session_state['iluminacion']
            st.metric("Dormitorio", st.session_state['iluminacion']["dormitorio"])

with calefaccion:
    st.subheader("Calefacción")
    controlCalefaccion=st.container()
    with controlCalefaccion:
        temperatura,calefaccion,controlTemperatura=st.columns([1,1,2])
        with temperatura:
            temp=st.metric("Temperatura",st.session_state['temperatura'])
        with controlTemperatura:
            valor=st.slider("Cambia la temperatura",-30,30,key="temperatura")

        if valor:
            url = 'https://'+hostCalefaccion+'/temperatura/{}'.format(valor)
            x = requests.post(url)
            st.session_state['calefaccion'] = x.text

        with calefaccion:
            cal = st.metric("Calefacción", st.session_state['calefaccion'])
with riego:
    st.subheader("Riego")
    controlRiego=st.container()
    with controlRiego:
        humedad,riego,controlHumedad=st.columns([1,1,2])
        with humedad:
            temp=st.metric("Humedad",st.session_state['humedad'])

        with controlHumedad:
            valor=st.slider("Cambia la humdedad",0,100,key="humedad")

        if valor:
            url = 'https://'+hostRiego+'/riego/{}'.format(valor)
            x = requests.post(url)
            st.session_state['estadoRiego'] = x.text

        with riego:
            cal = st.metric("Riego", st.session_state['estadoRiego'])
with alertas:
    banner=st.empty()
    dispositivos, control = st.columns(2)

    with control:
        tiempoEspera=st.slider("Tiempo encendido",0,90,value=0)

    expand=st.expander("Agregar dispositivos")
    with expand:
        st.session_state['lista_dispositivos']=st_tags(label="Dispositivos", value=st.session_state['lista_dispositivos'],key='1',maxtags = 4)

    with dispositivos:
        disp=st.radio("Dispositivos",st.session_state['lista_dispositivos'],key="disp")

    if tiempoEspera:

        url = 'https://'+hostControl+'/aparato/tiempo/'+str(tiempoEspera)
        x = requests.get(url)
        data = x.json()
        st.session_state['estadoAlerta'] = str(dict(data).get("accion"))

    with banner:
        if st.session_state['estadoAlerta']=="apagar" and st.session_state['estadoAlerta'] is not None:
            st.error("Apagar dispositivo por seguridad")
        else:
            st.success("Mantener encendido")