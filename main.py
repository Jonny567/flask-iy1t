from flask import Flask, request, render_template, jsonify
from samsungctl import Remote
from lg import Remote as lgremote
from bravia import TV,TVConfig
from tcl import TCLTVRemote
from haier import HaierTVRemote
from hisense import HisenseTv
from pairing import PairingSocket
from sending_keys import SendingKeySocket
from key_codes import *
import socket
import re

import argparse
import asyncio
import logging
from typing import cast

from zeroconf import ServiceStateChange, Zeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from androidtvremote2 import (
    AndroidTVRemote,
    CannotConnect,
    ConnectionClosed,
    InvalidAuth,
)

app = Flask(__name__)

samsung_arr = []
samsung_selectedDevice = False
samsung_remote = None
samsung_tv_state = "off"


lg_remote = None
lg_tv_state= "off"


sony_remote = None
sony_tv_state= "off"

tcl_remote = None
tcl_tv_state= "off"

haier_remote = None
haier_tv_state= "off"

hisense_remote = None
hisense_tv_state= "off"

hitachi_remote = None
hitachi_ip = None

linsar_remote = None
linsar_ip = None

sanyo_remote = None
sanyo_ip = None

mibox_remote = None
mibox_ip = None

oneplus_remote = None
oneplus_ip = None

sansui_remote = None
sansui_ip = None


toshiba_remote = None
toshiba_ip = None

panasonic_remote = None
panasonic_ip = None

vizio_remote = None
vizio_ip = None

philips_remote = None
philips_ip = None

thomson_remote = None
thomson_ip = None

aconatic_remote = None
aconatic_ip = None

asus_remote = None
asus_ip = None

asanzo_remote = None
asanzo_ip = None

casper_remote = None
casper_ip = None

tclandroid_remote = None
tclandroid_ip = None





_LOGGER = logging.getLogger(__name__)


async def _host_from_zeroconf(timeout: float) -> str:
    def _async_on_service_state_change(
        zeroconf: Zeroconf,
        service_type: str,
        name: str,
        state_change: ServiceStateChange,
    ) -> None:
        if state_change is not ServiceStateChange.Added:
            return
        _ = asyncio.ensure_future(
            async_display_service_info(zeroconf, service_type, name)
        )

    async def async_display_service_info(
        zeroconf: Zeroconf, service_type: str, name: str
    ) -> None:
        info = AsyncServiceInfo(service_type, name)
        await info.async_request(zeroconf, 3000)
        if info:
            addresses = [
                "%s:%d" % (addr, cast(int, info.port))
                for addr in info.parsed_scoped_addresses()
            ]
            print("  Name: %s" % name)
            print("  Addresses: %s" % ", ".join(addresses))
            if info.properties:
                print("  Properties:")
                for key, value in info.properties.items():
                    print("    %s: %s", key, value)
            else:
                print("  No properties")
        else:
            print("  No info")
        print()

    zc = AsyncZeroconf()
    services = ["_androidtvremote2._tcp.local."]
    print(
        f"\nBrowsing {services} service(s) for {timeout} seconds, press Ctrl-C to exit...\n"
    )
    browser = AsyncServiceBrowser(
        zc.zeroconf, services, handlers=[_async_on_service_state_change]
    )
    await asyncio.sleep(timeout)

    await browser.async_cancel()
    return await zc.async_close()


async def _pair(remote: AndroidTVRemote,code) -> None:
    while True:
        pairing_code = code
        try:
            return await remote.async_finish_pairing(pairing_code)
        except InvalidAuth as exc:
            _LOGGER.error("Invalid pairing code. Error: %s", exc)
            continue
        except ConnectionClosed as exc:
            _LOGGER.error("Initialize pair again. Error: %s", exc)
            return await _pair(remote,pairing_code)



def find_tvs(searchis,attempts=5, first_only=True):
        request = 'M-SEARCH * HTTP/1.1\r\n' \
                  'HOST: 239.255.255.250:1900\r\n' \
                  'MAN: "ssdp:discover"\r\n' \
                  'MX: 2\r\n' \
                  'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)

        addresses = []
        while attempts > 0:
            sock.sendto(request.encode('UTF-8'), ('239.255.255.250', 1900))
            try:
                response, address = sock.recvfrom(512)
            except:
                attempts -= 1
                continue

            if re.search(searchis, response):
                if first_only:
                    sock.close()
                    return address[0]
                else:
                    addresses.append(address[0])

            attempts -= 1

        sock.close()
        if first_only:
            raise Remote.NoTVFound
        else:
            if len(addresses) == 0:
                raise Remote.NoTVFound
            else:
                return addresses


@app.route('/')
def hello_world():
    return render_template("tvselect.html")

@app.route('/samsung')
def samsung():
    return render_template("samsung.html")


@app.route('/samsung-send-ip', methods=['POST'])
def handle_button_press2():
    global samsung_selectedDevice, samsung_remote
    data = request.get_json()
    samsung_selectedDevice = data.get('ip')
    if(samsung_selectedDevice=="no"):
        samsung_selectedDevice=find_tvs("samsung")

    # Configure the Samsung TV remote
    config = {
        "name": "samsungctl",  # Give your remote a name
        "description": "PC",
        "id": "",
        "host": samsung_selectedDevice,
        "port": 55000,
        "method": "legacy",
        "timeout": 9,
    }
    samsung_remote = Remote(config)

    response_message = f'Successfully configured remote for Samsung TV at IP: {samsung_selectedDevice}'

    return jsonify(response=response_message)

@app.route('/samsung-button-pressed', methods=['POST'])
def handle_button_press():
    data = request.get_json()
    button_class = data.get('buttonClass')
    global samsung_remote
    global samsung_tv_state

    if samsung_remote:
        if button_class == 'power':
            if samsung_tv_state == "off":
                samsung_tv_state = "on"
                samsung_remote.control("KEY_POWERON")
            else:
                samsung_remote.control("KEY_POWEROFF")
                samsung_tv_state = "off"
        elif button_class == 'back':
            samsung_remote.control("KEY_RETURN")
        elif button_class == 'info':
            samsung_remote.control("KEY_INFO")
        elif button_class == 'tools':
            samsung_remote.control("KEY_TOOLS")
        elif button_class == 'guide':
            samsung_remote.control("KEY_GUIDE")
        elif button_class == 'exit':
            samsung_remote.control("KEY_RETURN")
        elif button_class == 'menu':
            samsung_remote.control("KEY_MENU")
        elif button_class == 'chlist':
            samsung_remote.control("KEY_CH_LIST")
        elif button_class == 'pannel':
            samsung_remote.control("KEY_PANNEL_CHDOWN")
        elif button_class == 'mute':
            samsung_remote.control("KEY_MUTE")
        elif button_class == 'volumeup':
            samsung_remote.control("KEY_VOLUP")
        elif button_class == 'volumedown':
            samsung_remote.control("KEY_VOLDOWN")
        elif button_class == 'channelup':
            samsung_remote.control("KEY_CHUP")
        elif button_class == 'channeldown':
            samsung_remote.control("KEY_CHDOWN")
        elif button_class == 'enter':
            samsung_remote.control("KEY_ENTER")
        elif button_class == 'goup':
            samsung_remote.control("KEY_UP")
        elif button_class == 'godown':
            samsung_remote.control("KEY_DOWN")
        elif button_class == 'goleft':
            samsung_remote.control("KEY_LEFT")
        elif button_class == 'goright':
            samsung_remote.control("KEY_RIGHT")
        elif button_class == 'one':
            samsung_remote.control("KEY_1")
        elif button_class == 'two':
            samsung_remote.control("KEY_2")
        elif button_class == 'three':
            samsung_remote.control("KEY_3")
        elif button_class == 'four':
            samsung_remote.control("KEY_4")
        elif button_class == 'five':
            samsung_remote.control("KEY_5")
        elif button_class == 'six':
            samsung_remote.control("KEY_6")
        elif button_class == 'seven':
            samsung_remote.control("KEY_7")
        elif button_class == 'eight':
            samsung_remote.control("KEY_8")
        elif button_class == 'nine':
            samsung_remote.control("KEY_9")
        elif button_class == 'zero':
            samsung_remote.control("KEY_0")
        elif button_class == 'f1':
            samsung_remote.control("KEY_RED")
        elif button_class == 'f2':
            samsung_remote.control("KEY_GREEN")
        elif button_class == 'f3':
            samsung_remote.control("KEY_YELLOW")
        elif button_class == 'f4':
            samsung_remote.control("KEY_BLUE")


        response_message = f'Successfully sent {button_class} command to the Samsung TV'
    else:
        response_message = 'Please configure the remote first using /samsung-send-ip'

    return jsonify(response=response_message)


@app.route('/lg')
def lg():

    return render_template("lg.html")

@app.route('/lg-send-key', methods=['POST'])
def lg_press3():
    global lg_remote
    address = lgremote.find_tvs(first_only=True)
    lg_remote = lgremote(address)
    lg_remote.request_pair()

    response_message = f'Successfully send pairing key'

    return jsonify(response=response_message)


@app.route('/lg-send-ip', methods=['POST'])
def lg_press2():
    global lg_remote
    data = request.get_json()
    lg_selectedDevice = data.get('ip')
    address = lgremote.find_tvs(first_only=True)
    lg_remote = lgremote(address)

    lg_remote.set_pairing_key(lg_selectedDevice)

    response_message = f'Successfully configured remote for LG TV at IP: {lg_selectedDevice}'

    return jsonify(response=response_message)


@app.route('/lg-button-pressed', methods=['POST'])
def lg_button_press():
    data = request.get_json()
    button_class = data.get('buttonClass')
    global lg_remote
    global lg_tv_state

    if lg_remote:
        if button_class == 'power':
            if lg_tv_state == "off":
                lg_remote.send_command(Remote.POWER)
                lg_tv_state = "on"
            else:
                lg_remote.send_command(Remote.POWER)
                lg_tv_state = "off"
        elif button_class == 'back':
            lg_remote.send_command(Remote.BACK)
        elif button_class == 'home':
            lg_remote.send_command(Remote.HOME)
        elif button_class == 'info':
            lg_remote.send_command(Remote.INFO)
        elif button_class == 'tools':
            lg_remote.send_command(Remote.QUICK_MENU)
        elif button_class == 'guide':
            lg_remote.send_command(Remote.INFO)
        elif button_class == 'exit':
            lg_remote.send_command(Remote.EXIT)
        elif button_class == 'menu':
            lg_remote.send_command(Remote.MENU)
        elif button_class == 'chlist':
            lg_remote.send_command(Remote.PROGRAM_LIST)
        elif button_class == 'pannel':
            lg_remote.send_command(Remote.PIP)
        elif button_class == 'mute':
            lg_remote.send_command(Remote.MUTE)
        elif button_class == 'volumeup':
            lg_remote.send_command(Remote.VOLUME_UP)
        elif button_class == 'volumedown':
            lg_remote.send_command(Remote.VOLUME_DOWN)
        elif button_class == 'channelup':
            lg_remote.send_command(Remote.CHANNEL_UP)
        elif button_class == 'channeldown':
            lg_remote.send_command(Remote.CHANNEL_DOWN)
        elif button_class == 'enter':
            lg_remote.send_command(Remote.OK)
        elif button_class == 'goup':
            lg_remote.send_command(Remote.UP)
        elif button_class == 'godown':
            lg_remote.send_command(Remote.DOWN)
        elif button_class == 'goleft':
            lg_remote.send_command(Remote.LEFT)
        elif button_class == 'goright':
            lg_remote.send_command(Remote.RIGHT)
        elif button_class == 'one':
            lg_remote.send_command(Remote.NUM_1)
        elif button_class == 'two':
            lg_remote.send_command(Remote.NUM_2)
        elif button_class == 'three':
            lg_remote.send_command(Remote.NUM_3)
        elif button_class == 'four':
            lg_remote.send_command(Remote.NUM_4)
        elif button_class == 'five':
            lg_remote.send_command(Remote.NUM_5)
        elif button_class == 'six':
            lg_remote.send_command(Remote.NUM_6)
        elif button_class == 'seven':
            lg_remote.send_command(Remote.NUM_7)
        elif button_class == 'eight':
            lg_remote.send_command(Remote.NUM_8)
        elif button_class == 'nine':
            lg_remote.send_command(Remote.NUM_9)
        elif button_class == 'zero':
            lg_remote.send_command(Remote.NUM_0)
        elif button_class == 'f1':
            lg_remote.send_command(Remote.RED)
        elif button_class == 'f2':
            lg_remote.send_command(Remote.GREEN)
        elif button_class == 'f3':
            lg_remote.send_command(Remote.YELLOW)
        elif button_class == 'f4':
            lg_remote.send_command(Remote.BLUE)


        response_message = f'Successfully sent {button_class} command to the LG TV'
    else:
        response_message = 'Please configure the remote first using /lg-send-ip'

    return jsonify(response=response_message)


@app.route('/sony')
def sony():
    return render_template("sony.html")

@app.route('/sony-send-ip', methods=['POST'])
def sony_press2():
    global sony_remote
    data = request.get_json()
    key = data.get('key')
    ip = data.get('ip')
    name = data.get('name')
    if(ip=="no"):
        ip=find_tvs("Sony")
        name="Sony"
    
    config = TVConfig(ip, name)
    sony_remote = TV.connect(config, key)

    response_message = f'Successfully configured remote for Sony TV at key: {key}'

    return jsonify(response=response_message)


@app.route('/sony-button-pressed', methods=['POST'])
def sony_button_press():
    data = request.get_json()
    button_class = data.get('buttonClass')
    global sony_remote

    if sony_remote:
        if button_class == 'power':
            if sony_remote.is_on():
                sony_remote.power_off()
            else:
                sony_remote.wake_up()
        elif button_class == 'back':
            sony_remote.back()
        elif button_class == 'home':
            sony_remote.home()
        elif button_class == 'info':
            sony_remote.help()
        elif button_class == 'tools':
            sony_remote.options()
        elif button_class == 'guide':
            sony_remote.options()
        elif button_class == 'exit':
            sony_remote.exit()
        elif button_class == 'menu':
            sony_remote.menu()
        elif button_class == 'chlist':
            sony_remote.display()
        elif button_class == 'pannel':
            sony_remote.display()
        elif button_class == 'mute':
            sony_remote.mute()
        elif button_class == 'volumeup':
            sony_remote.volume_up()
        elif button_class == 'volumedown':
            sony_remote.volume_down()
        elif button_class == 'channelup':
            sony_remote.channelup()
        elif button_class == 'channeldown':
            sony_remote.channeldown()
        elif button_class == 'enter':
            sony_remote.confirm()
        elif button_class == 'goup':
            sony_remote.up()
        elif button_class == 'godown':
            sony_remote.down()
        elif button_class == 'goleft':
            sony_remote.left()
        elif button_class == 'goright':
            sony_remote.right()
        elif button_class == 'one':
            sony_remote.one()
        elif button_class == 'two':
            sony_remote.two()
        elif button_class == 'three':
            sony_remote.three()
        elif button_class == 'four':
            sony_remote.four()
        elif button_class == 'five':
            sony_remote.five()
        elif button_class == 'six':
            sony_remote.six()
        elif button_class == 'seven':
            sony_remote.seven()
        elif button_class == 'eight':
            sony_remote.eight()
        elif button_class == 'nine':
            sony_remote.nine()
        elif button_class == 'zero':
            sony_remote.zero()
        elif button_class == 'f1':
            sony_remote.f1()
        elif button_class == 'f2':
            sony_remote.f2()
        elif button_class == 'f3':
            sony_remote.f3()
        elif button_class == 'f4':
            sony_remote.f4()

        response_message = f'Successfully sent {button_class} command to the LG TV'
    else:
        response_message = 'Please configure the remote first using /lg-send-ip'

    return jsonify(response=response_message)


@app.route('/tcl')
def tcl():
    return render_template("tcl.html")

@app.route('/tcl-send-ip', methods=['POST'])
def tcl_press2():
    global tcl_remote
    tcl_remote=TCLTVRemote()
    tcl_remote.connect()

    response_message = f'Successfully configured remote for Sony TV at key: {tcl_remote}'

    return jsonify(response=response_message)

@app.route('/tcl-button-pressed', methods=['POST'])
def tcl_button_press():
    data = request.get_json()
    button_class = data.get('buttonClass')
    global tcl_remote
    tcl_remote.start_keep_alive()
    if tcl_remote:
        if button_class == 'back':
            tcl_remote.keypress("TR_KEY_BACK")
        elif button_class == 'info':
            tcl_remote.keypress("TR_KEY_INFOWINDOW")
        elif button_class == 'guide':
            tcl_remote.keypress("TR_KEY_GUIDE")
        elif button_class == 'exit':
            tcl_remote.keypress("TR_KEY_EXIT")
        elif button_class == 'menu':
            tcl_remote.keypress("TR_KEY_MAINMENU")
        elif button_class == 'chlist':
            tcl_remote.keypress("TR_KEY_LIST")
        elif button_class == 'pannel':
            tcl_remote.keypress("TR_KEY_OPTION")
        elif button_class == 'mute':
            tcl_remote.keypress("TR_KEY_MUTE")
        elif button_class == 'volumeup':
            tcl_remote.keypress("TR_KEY_VOL_UP")
        elif button_class == 'volumedown':
            tcl_remote.keypress("TR_KEY_VOL_DOWN")
        elif button_class == 'channelup':
            tcl_remote.keypress("TR_KEY_CH_UP")
        elif button_class == 'channeldown':
            tcl_remote.keypress("TR_KEY_CH_DOWN")
        elif button_class == 'enter':
            tcl_remote.keypress("TR_KEY_OK")
        elif button_class == 'goup':
            tcl_remote.keypress("TR_KEY_UP")
        elif button_class == 'godown':
            tcl_remote.keypress("TR_KEY_DOWN")
        elif button_class == 'goleft':
            tcl_remote.keypress("TR_KEY_LEFT")
        elif button_class == 'goright':
            tcl_remote.keypress("TR_KEY_RIGHT")
        elif button_class == 'one':
            tcl_remote.keypress("TR_KEY_1")
        elif button_class == 'two':
            tcl_remote.keypress("TR_KEY_2")
        elif button_class == 'three':
            tcl_remote.keypress("TR_KEY_3")
        elif button_class == 'four':
            tcl_remote.keypress("TR_KEY_4")
        elif button_class == 'five':
            tcl_remote.keypress("TR_KEY_5")
        elif button_class == 'six':
            tcl_remote.keypress("TR_KEY_6")
        elif button_class == 'seven':
            tcl_remote.keypress("TR_KEY_7")
        elif button_class == 'eight':
            tcl_remote.keypress("TR_KEY_8")
        elif button_class == 'nine':
            tcl_remote.keypress("TR_KEY_9")
        elif button_class == 'zero':
            tcl_remote.keypress("TR_KEY_ECO")
        elif button_class == 'f1':
            tcl_remote.keypress("TR_KEY_RED")
        elif button_class == 'f2':
            tcl_remote.keypress("TR_KEY_GREEN")
        elif button_class == 'f3':
            tcl_remote.keypress("TR_KEY_YELLOW")
        elif button_class == 'f4':
            tcl_remote.keypress("TR_KEY_BLUE")

        response_message = f'Successfully sent {button_class} command to the LG TV'
    else:
        response_message = 'Please configure the remote first using /lg-send-ip'

    return jsonify(response=response_message)

@app.route('/haier')
def haier():
    return render_template("haier.html")

@app.route('/haier-send-ip', methods=['POST'])
def haier_press2():
    global haier_remote
    data = request.get_json()
    haierip = data.get('ip')
    if(haierip=="no"):
        haierip=find_tvs("Haier")

    haier_remote=HaierTVRemote(haierip)
    haier_remote.open_connection()

    response_message = f'Successfully configured remote for Sony TV at key: {haierip}'

    return jsonify(response=response_message)


@app.route('/haier-button-pressed', methods=['POST'])
def haier_button_press():
    data = request.get_json()
    button_class = data.get('buttonClass')
    global haier_remote

    if haier_remote:
        if button_class == 'power':
            haier_remote.send_command(1012)
        elif button_class == 'back':
            haier_remote.send_command(1010)
        elif button_class == 'info':
            haier_remote.send_command(1018)
        elif button_class == 'tools':
            haier_remote.send_command(1067)
        elif button_class == 'guide':
            haier_remote.send_command(1047)
        elif button_class == 'exit':
            haier_remote.send_command(1037)
        elif button_class == 'menu':
            haier_remote.send_command(1048)
        elif button_class == 'chlist':
            haier_remote.send_command(1053)
        elif button_class == 'pannel':
            haier_remote.send_command(1067)
        elif button_class == 'mute':
            haier_remote.send_command(1013)
        elif button_class == 'volumeup':
            haier_remote.send_command(1016)
        elif button_class == 'volumedown':
            haier_remote.send_command(1017)
        elif button_class == 'channelup':
            haier_remote.send_command(1032)
        elif button_class == 'channeldown':
            haier_remote.send_command(1033)
        elif button_class == 'enter':
            haier_remote.send_command(1053)
        elif button_class == 'goup':
            haier_remote.send_command(1020)
        elif button_class == 'godown':
            haier_remote.send_command(1019)
        elif button_class == 'goleft':
            haier_remote.send_command(1021)
        elif button_class == 'goright':
            haier_remote.send_command(1022)
        elif button_class == 'one':
            haier_remote.send_command(1001)
        elif button_class == 'two':
            haier_remote.send_command(1002)
        elif button_class == 'three':
            haier_remote.send_command(1003)
        elif button_class == 'four':
            haier_remote.send_command(1004)
        elif button_class == 'five':
            haier_remote.send_command(1005)
        elif button_class == 'six':
            haier_remote.send_command(1006)
        elif button_class == 'seven':
            haier_remote.send_command(1007)
        elif button_class == 'eight':
            haier_remote.send_command(1008)
        elif button_class == 'nine':
            haier_remote.send_command(1009)
        elif button_class == 'zero':
            haier_remote.send_command(1000)
        elif button_class == 'f1':
            haier_remote.send_command(1055)
        elif button_class == 'f2':
            haier_remote.send_command(1054)
        elif button_class == 'f3':
            haier_remote.send_command(1050)
        elif button_class == 'f4':
            haier_remote.send_command(1052)
        elif button_class == 'netflix':
            haier_remote.send_command(1064)
        elif button_class == 'youtube':
            haier_remote.send_command(1062)

        response_message = f'Successfully sent {button_class} command to the Haier TV'
    else:
        response_message = 'Please configure the remote first using /haier-send-ip'

    return jsonify(response=response_message)


@app.route('/hisense')
def hisense():
    return render_template("hisense.html")

@app.route('/hisense-send-ip', methods=['POST'])
def hisense_press2():
    global hisense_remote
    data = request.get_json()
    hisenseip = data.get('ip')
    if(hisenseip=="no"):
        hisenseip=find_tvs("Hisense")
    hisense_remote=HisenseTv(hostname=hisenseip)
    response_message = f'Successfully configured remote for Sony TV at key: {hisenseip}'

    return jsonify(response=response_message)


@app.route('/hisense-button-pressed', methods=['POST'])
def hisense_button_press():
    data = request.get_json()
    button_class = data.get('buttonClass')
    global hisense_remote

    if hisense_remote.connected:
        if button_class == 'power':
            hisense_remote.send_key_power()
        elif button_class == 'home':
            hisense_remote.send_key_home()
        elif button_class == 'back':
            hisense_remote.send_key_back()
        elif button_class == 'info':
            hisense_remote.send_key_menu()
        elif button_class == 'tools':
            hisense_remote.send_key_mrmc()
        elif button_class == 'guide':
            hisense_remote.send_key_menu()
        elif button_class == 'exit':
            hisense_remote.send_key_exit()
        elif button_class == 'menu':
            hisense_remote.send_key_menu()
        elif button_class == 'mute':
            hisense_remote.send_key_menu()
        elif button_class == 'volumeup':
            hisense_remote.send_key_volume_up()
        elif button_class == 'volumedown':
            hisense_remote.send_key_volume_down()
        elif button_class == 'channelup':
            hisense_remote.send_key_channel_up()
        elif button_class == 'channeldown':
            hisense_remote.send_key_channel_down()
        elif button_class == 'enter':
            hisense_remote.send_key_ok()
        elif button_class == 'goup':
            hisense_remote.send_key_up()
        elif button_class == 'godown':
            hisense_remote.send_key_down()
        elif button_class == 'goleft':
            hisense_remote.send_key_left()
        elif button_class == 'goright':
            hisense_remote.send_key_right()
        elif button_class == 'one':
            hisense_remote.send_key_1()
        elif button_class == 'two':
            hisense_remote.send_key_2()
        elif button_class == 'three':
            hisense_remote.send_key_3()
        elif button_class == 'four':
            hisense_remote.send_key_4()
        elif button_class == 'five':
            hisense_remote.send_key_5()
        elif button_class == 'six':
            hisense_remote.send_key_6()
        elif button_class == 'seven':
            hisense_remote.send_key_7()
        elif button_class == 'eight':
            hisense_remote.send_key_8()
        elif button_class == 'nine':
            hisense_remote.send_key_9()
        elif button_class == 'zero':
            hisense_remote.send_key_0()
        elif button_class == 'f1':
            hisense_remote.send_key_source_1()
        elif button_class == 'f2':
            hisense_remote.send_key_source_2()
        elif button_class == 'f3':
            hisense_remote.send_key_source_3()
        elif button_class == 'f4':
            hisense_remote.send_key_source_4()
        elif button_class == 'netflix':
            hisense_remote.send_key_netflix()
        elif button_class == 'youtube':
            hisense_remote.send_key_youtube()
        elif button_class == 'disney':
            hisense_remote.send_key_disneyplus()
        elif button_class == 'amazon':
            hisense_remote.send_key_amazon()

        response_message = f'Successfully sent {button_class} command to the Haier TV'
    else:
        response_message = 'Please configure the remote first using /haier-send-ip'

    return jsonify(response=response_message)


@app.route('/hitachi')
def hitachi():
    return render_template("hitachi.html")

@app.route('/hitachi-send-ip', methods=['POST'])
def hitachi_press2():
    global hitachi_remote
    global hitachi_ip
    data = request.get_json()
    hitachiip = data.get('ip')
    if(hitachiip=="no"):
        hitachiip=find_tvs("Hitachi")
    hitachi_ip=hitachiip
    pairing_sock = PairingSocket("hmi", hitachiip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote for Sony TV at key: {hitachiip}'

    return jsonify(response=response_message)


@app.route('/hitachi-button-pressed', methods=['POST'])
def hitachi_button_press():
    global hitachi_remote
    global hitachi_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    hitachi_remote = SendingKeySocket("Hitachi TV", hitachi_ip)
    hitachi_remote.connect()

    if hitachi_remote:
        if button_class == 'power':
            hitachi_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            hitachi_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            hitachi_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            hitachi_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            hitachi_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            hitachi_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            hitachi_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            hitachi_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            hitachi_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            hitachi_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            hitachi_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            hitachi_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            hitachi_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            hitachi_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            hitachi_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            hitachi_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            hitachi_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            hitachi_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            hitachi_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            hitachi_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            hitachi_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            hitachi_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            hitachi_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            hitachi_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            hitachi_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            hitachi_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            hitachi_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            hitachi_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            hitachi_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            hitachi_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            hitachi_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            hitachi_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command to the Haier TV'
    else:
        response_message = 'Please configure the remote first using /haier-send-ip'

    return jsonify(response=response_message)

@app.route('/linsar')
def linsar():
    return render_template("linsar.html")

@app.route('/linsar-send-ip', methods=['POST'])
def linsar_press2():
    global linsar_remote
    global linsar_ip
    data = request.get_json()
    linsarip = data.get('ip')
    if(linsarip=="no"):
        linsarip=find_tvs("Hitachi")
    linsar_ip=linsarip
    pairing_sock = PairingSocket("hmi", linsarip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote for Sony TV at key: {linsarip}'

    return jsonify(response=response_message)

@app.route('/linsar-button-pressed', methods=['POST'])
def linsar_button_press():
    global linsar_remote
    global linsar_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    linsar_remote = SendingKeySocket("Linsar TV", linsar_ip)
    linsar_remote.connect()

    if linsar_remote:
        if button_class == 'power':
            linsar_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            linsar_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            linsar_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            linsar_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            linsar_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            linsar_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            linsar_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            linsar_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            linsar_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            linsar_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            linsar_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            linsar_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            linsar_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            linsar_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            linsar_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            linsar_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            linsar_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            linsar_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            linsar_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            linsar_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            linsar_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            linsar_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            linsar_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            linsar_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            linsar_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            linsar_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            linsar_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            linsar_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            linsar_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            linsar_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            linsar_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            linsar_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)

@app.route('/sanyotv')
def sanyo():
    return render_template("sanyo.html")

@app.route('/sanyo-send-ip', methods=['POST'])
def sanyo_press2():
    global sanyo_remote
    global sanyo_ip
    data = request.get_json()
    sanyoip = data.get('ip')
    if(sanyoip=="no"):
        sanyoip=find_tvs("Sanyo")
    sanyo_ip=sanyoip
    pairing_sock = PairingSocket("hmi", sanyoip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote for Sony TV at key: {sanyoip}'

    return jsonify(response=response_message)

@app.route('/sanyo-button-pressed', methods=['POST'])
def sanyo_button_press():
    global sanyo_remote
    global sanyo_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    sanyo_remote = SendingKeySocket("Sanyo TV", sanyo_ip)
    sanyo_remote.connect()

    if sanyo_remote:
        if button_class == 'power':
            sanyo_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            sanyo_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            sanyo_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            sanyo_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            sanyo_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            sanyo_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            sanyo_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            sanyo_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            sanyo_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            sanyo_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            sanyo_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            sanyo_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            sanyo_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            sanyo_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            sanyo_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            sanyo_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            sanyo_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            sanyo_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            sanyo_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            sanyo_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            sanyo_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            sanyo_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            sanyo_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            sanyo_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            sanyo_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            sanyo_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            sanyo_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            sanyo_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            sanyo_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            sanyo_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            sanyo_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            sanyo_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/mibox')
def mibox():
    return render_template("mibox.html")

@app.route('/mibox-send-ip', methods=['POST'])
def mibox_press2():
    global mibox_remote
    global mibox_ip
    data = request.get_json()
    miboxip = data.get('ip')
    if(miboxip=="no"):
        miboxip=find_tvs("Mi Box")
    mibox_ip=miboxip
    pairing_sock = PairingSocket("hmi", miboxip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote for Sony TV at key: {miboxip}'

    return jsonify(response=response_message)


@app.route('/mibox-button-pressed', methods=['POST'])
def mibox_button_press():
    global mibox_remote
    global mibox_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    mibox_remote = SendingKeySocket("Mi Box", mibox_ip)
    mibox_remote.connect()

    if mibox_remote:
        if button_class == 'power':
            mibox_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            mibox_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            mibox_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            mibox_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            mibox_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            mibox_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            mibox_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            mibox_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            mibox_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            mibox_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            mibox_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            mibox_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            mibox_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            mibox_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            mibox_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            mibox_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            mibox_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            mibox_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            mibox_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            mibox_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            mibox_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            mibox_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            mibox_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            mibox_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            mibox_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            mibox_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            mibox_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            mibox_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            mibox_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            mibox_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            mibox_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            mibox_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)




@app.route('/oneplus')
def oneplus():
    return render_template("oneplus.html")


@app.route('/oneplus-send-key', methods=['POST'])
async def oneplus_press3():
    global oneplus_remote
    global oneplus_ip
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="IP address of Android TV to connect to")
    parser.add_argument(
        "--certfile",
        help="filename that contains the client certificate in PEM format",
        default="cert.pem",
    )
    parser.add_argument(
        "--keyfile",
        help="filename that contains the public key in PEM format",
        default="key.pem",
    )
    parser.add_argument(
        "--client_name",
        help="shown on the Android TV during pairing",
        default="Android TV Remote demo",
    )
    parser.add_argument(
        "--scan_timeout",
        type=float,
        help="zeroconf scan timeout in seconds",
        default=10,
    )
    parser.add_argument(
        "-v", "--verbose", help="enable verbose logging", action="store_true"
    )
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # host = await _host_from_zeroconf(args.scan_timeout)
    host=False
    if(host):
        oneplus_ip=host
    else:
        # host=find_tvs("OnePlus")
        host="192.168.3.4"
        oneplus_ip=host

    oneplus_remote = AndroidTVRemote(args.client_name, args.certfile, args.keyfile, host)
    if await oneplus_remote.async_generate_cert_if_missing():
        await oneplus_remote.async_start_pairing()
    return "oneplus-press3 response"

@app.route('/oneplus-send-ip', methods=['POST'])
async def oneplus_press2():
    global oneplus_remote
    global oneplus_ip
    data = request.get_json()
    code = data.get('ip')
    await _pair(oneplus_remote, code)
    while True:
        try:
            await oneplus_remote.async_connect()
            break
        except InvalidAuth as exc:
            await _pair(oneplus_remote,code)
        except (CannotConnect, ConnectionClosed) as exc:
            _LOGGER.error("Cannot connect, exiting. Error: %s", exc)
            return "Cannot connect, exiting. Error: " + str(exc)

    oneplus_remote.keep_reconnecting()

    response_message = "Successfully configured remote"
    return jsonify(response=response_message)



@app.route('/oneplus-button-pressed', methods=['POST'])
def oneplus_button_press():
    global oneplus_remote
    data = request.get_json()
    button_class = data.get('buttonClass')
    if oneplus_remote:
        if button_class == 'power':
            oneplus_remote.send_key_command("POWER")
        elif button_class == 'home':
            oneplus_remote.send_key_command("HOME")
        elif button_class == 'back':
            oneplus_remote.send_key_command("BACK")
        elif button_class == 'info':
            oneplus_remote.send_key_command("INFO")
        elif button_class == 'tools':
            oneplus_remote.send_key_command("EXPLORER")
        elif button_class == 'guide':
            oneplus_remote.send_key_command("GUIDE")
        elif button_class == 'menu':
            oneplus_remote.send_key_command("MENU")
        elif button_class == 'mute':
            oneplus_remote.send_key_command("VOLUME_MUTE")
        elif button_class == 'volumeup':
            oneplus_remote.send_key_command("VOLUME_UP")
        elif button_class == 'volumedown':
            oneplus_remote.send_key_command("VOLUME_DOWN")
        elif button_class == 'channelup':
            oneplus_remote.send_key_command("CHANNEL_UP")
        elif button_class == 'channeldown':
            oneplus_remote.send_key_command("CHANNEL_DOWN")
        elif button_class == 'enter':
            oneplus_remote.send_key_command("ENTER")
        elif button_class == 'goup':
            oneplus_remote.send_key_command("DPAD_UP")
        elif button_class == 'godown':
            oneplus_remote.send_key_command("DPAD_DOWN")
        elif button_class == 'goleft':
            oneplus_remote.send_key_command("DPAD_LEFT")
        elif button_class == 'goright':
            oneplus_remote.send_key_command("DPAD_RIGHT")
        elif button_class == 'one':
            oneplus_remote.send_key_command("1")
        elif button_class == 'two':
            oneplus_remote.send_key_command("2")
        elif button_class == 'three':
            oneplus_remote.send_key_command("3")
        elif button_class == 'four':
            oneplus_remote.send_key_command("4")
        elif button_class == 'five':
            oneplus_remote.send_key_command("5")
        elif button_class == 'six':
            oneplus_remote.send_key_command("6")
        elif button_class == 'seven':
            oneplus_remote.send_key_command("7")
        elif button_class == 'eight':
            oneplus_remote.send_key_command("8")
        elif button_class == 'nine':
            oneplus_remote.send_key_command("9")
        elif button_class == 'zero':
            oneplus_remote.send_key_command("0")
        elif button_class == 'f1':
            oneplus_remote.send_key_command("F1")
        elif button_class == 'f2':
            oneplus_remote.send_key_command("F2")
        elif button_class == 'f3':
            oneplus_remote.send_key_command("F3")
        elif button_class == 'f4':
            oneplus_remote.send_key_command("F4")
        elif button_class == 'netflix':
            oneplus_remote.send_launch_app_command("https://www.netflix.com/title")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/sansui')
def sansui():
    return render_template("sansui.html")


@app.route('/sansui-send-key', methods=['POST'])
async def sansui_press3():
    global sansui_remote
    global sansui_ip
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="IP address of Android TV to connect to")
    parser.add_argument(
        "--certfile",
        help="filename that contains the client certificate in PEM format",
        default="cert.pem",
    )
    parser.add_argument(
        "--keyfile",
        help="filename that contains the public key in PEM format",
        default="key.pem",
    )
    parser.add_argument(
        "--client_name",
        help="shown on the Android TV during pairing",
        default="Android TV Remote demo",
    )
    parser.add_argument(
        "--scan_timeout",
        type=float,
        help="zeroconf scan timeout in seconds",
        default=10,
    )
    parser.add_argument(
        "-v", "--verbose", help="enable verbose logging", action="store_true"
    )
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    host = await _host_from_zeroconf(args.scan_timeout)
    if(host):
        sansui_ip=host
    else:
        host=find_tvs("Sansui")
        sansui_ip=host

    sansui_remote = AndroidTVRemote(args.client_name, args.certfile, args.keyfile, host)
    if await sansui_remote.async_generate_cert_if_missing():
        await sansui_remote.async_start_pairing()
    return "sansui-press3 response"



@app.route('/sansui-send-ip', methods=['POST'])
async def sansui_press2():
    global sansui_remote
    global sansui_ip
    data = request.get_json()
    code = data.get('ip')
    await _pair(sansui_remote, code)
    while True:
        try:
            await sansui_remote.async_connect()
            break
        except InvalidAuth as exc:
            await _pair(sansui_remote,code)
        except (CannotConnect, ConnectionClosed) as exc:
            _LOGGER.error("Cannot connect, exiting. Error: %s", exc)
            return "Cannot connect, exiting. Error: " + str(exc)

    sansui_remote.keep_reconnecting()

    response_message = "Successfully configured remote"
    return jsonify(response=response_message)


@app.route('/sansui-button-pressed', methods=['POST'])
def sansui_button_press():
    global sansui_remote
    data = request.get_json()
    button_class = data.get('buttonClass')
    if sansui_remote:
        if button_class == 'power':
            sansui_remote.send_key_command("POWER")
        elif button_class == 'home':
            sansui_remote.send_key_command("HOME")
        elif button_class == 'back':
            sansui_remote.send_key_command("BACK")
        elif button_class == 'info':
            sansui_remote.send_key_command("INFO")
        elif button_class == 'tools':
            sansui_remote.send_key_command("EXPLORER")
        elif button_class == 'guide':
            sansui_remote.send_key_command("GUIDE")
        elif button_class == 'menu':
            sansui_remote.send_key_command("MENU")
        elif button_class == 'mute':
            sansui_remote.send_key_command("VOLUME_MUTE")
        elif button_class == 'volumeup':
            sansui_remote.send_key_command("VOLUME_UP")
        elif button_class == 'volumedown':
            sansui_remote.send_key_command("VOLUME_DOWN")
        elif button_class == 'channelup':
            sansui_remote.send_key_command("CHANNEL_UP")
        elif button_class == 'channeldown':
            sansui_remote.send_key_command("CHANNEL_DOWN")
        elif button_class == 'enter':
            sansui_remote.send_key_command("ENTER")
        elif button_class == 'goup':
            sansui_remote.send_key_command("DPAD_UP")
        elif button_class == 'godown':
            sansui_remote.send_key_command("DPAD_DOWN")
        elif button_class == 'goleft':
            sansui_remote.send_key_command("DPAD_LEFT")
        elif button_class == 'goright':
            sansui_remote.send_key_command("DPAD_RIGHT")
        elif button_class == 'one':
            sansui_remote.send_key_command("1")
        elif button_class == 'two':
            sansui_remote.send_key_command("2")
        elif button_class == 'three':
            sansui_remote.send_key_command("3")
        elif button_class == 'four':
            sansui_remote.send_key_command("4")
        elif button_class == 'five':
            sansui_remote.send_key_command("5")
        elif button_class == 'six':
            sansui_remote.send_key_command("6")
        elif button_class == 'seven':
            sansui_remote.send_key_command("7")
        elif button_class == 'eight':
            sansui_remote.send_key_command("8")
        elif button_class == 'nine':
            sansui_remote.send_key_command("9")
        elif button_class == 'zero':
            sansui_remote.send_key_command("0")
        elif button_class == 'f1':
            sansui_remote.send_key_command("F1")
        elif button_class == 'f2':
            sansui_remote.send_key_command("F2")
        elif button_class == 'f3':
            sansui_remote.send_key_command("F3")
        elif button_class == 'f4':
            sansui_remote.send_key_command("F4")
        elif button_class == 'netflix':
            sansui_remote.send_launch_app_command("https://www.netflix.com/title")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)



@app.route('/toshiba')
def toshiba():
    return render_template("toshiba.html")

@app.route('/toshiba-send-key', methods=['POST'])
async def toshiba_press3():
    global toshiba_remote
    global toshiba_ip
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="IP address of Android TV to connect to")
    parser.add_argument(
        "--certfile",
        help="filename that contains the client certificate in PEM format",
        default="cert.pem",
    )
    parser.add_argument(
        "--keyfile",
        help="filename that contains the public key in PEM format",
        default="key.pem",
    )
    parser.add_argument(
        "--client_name",
        help="shown on the Android TV during pairing",
        default="Android TV Remote demo",
    )
    parser.add_argument(
        "--scan_timeout",
        type=float,
        help="zeroconf scan timeout in seconds",
        default=10,
    )
    parser.add_argument(
        "-v", "--verbose", help="enable verbose logging", action="store_true"
    )
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    host = await _host_from_zeroconf(args.scan_timeout)
    if(host):
        toshiba_ip=host
    else:
        host=find_tvs("Toshiba")
        toshiba_ip=host

    toshiba_remote = AndroidTVRemote(args.client_name, args.certfile, args.keyfile, host)
    if await toshiba_remote.async_generate_cert_if_missing():
        await toshiba_remote.async_start_pairing()
    return "toshiba-press3 response"



@app.route('/toshiba-send-ip', methods=['POST'])
async def toshiba_press2():
    global toshiba_remote
    global toshiba_ip
    data = request.get_json()
    code = data.get('ip')
    await _pair(toshiba_remote, code)
    while True:
        try:
            await toshiba_remote.async_connect()
            break
        except InvalidAuth as exc:
            await _pair(toshiba_remote,code)
        except (CannotConnect, ConnectionClosed) as exc:
            _LOGGER.error("Cannot connect, exiting. Error: %s", exc)
            return "Cannot connect, exiting. Error: " + str(exc)

    toshiba_remote.keep_reconnecting()

    response_message = "Successfully configured remote"
    return jsonify(response=response_message)




@app.route('/toshiba-button-pressed', methods=['POST'])
def toshiba_button_press():
    global toshiba_remote
    data = request.get_json()
    button_class = data.get('buttonClass')
    if toshiba_remote:
        if button_class == 'power':
            toshiba_remote.send_key_command("POWER")
        elif button_class == 'home':
            toshiba_remote.send_key_command("HOME")
        elif button_class == 'back':
            toshiba_remote.send_key_command("BACK")
        elif button_class == 'info':
            toshiba_remote.send_key_command("INFO")
        elif button_class == 'tools':
            toshiba_remote.send_key_command("EXPLORER")
        elif button_class == 'guide':
            toshiba_remote.send_key_command("GUIDE")
        elif button_class == 'menu':
            toshiba_remote.send_key_command("MENU")
        elif button_class == 'mute':
            toshiba_remote.send_key_command("VOLUME_MUTE")
        elif button_class == 'volumeup':
            toshiba_remote.send_key_command("VOLUME_UP")
        elif button_class == 'volumedown':
            toshiba_remote.send_key_command("VOLUME_DOWN")
        elif button_class == 'channelup':
            toshiba_remote.send_key_command("CHANNEL_UP")
        elif button_class == 'channeldown':
            toshiba_remote.send_key_command("CHANNEL_DOWN")
        elif button_class == 'enter':
            toshiba_remote.send_key_command("ENTER")
        elif button_class == 'goup':
            toshiba_remote.send_key_command("DPAD_UP")
        elif button_class == 'godown':
            toshiba_remote.send_key_command("DPAD_DOWN")
        elif button_class == 'goleft':
            toshiba_remote.send_key_command("DPAD_LEFT")
        elif button_class == 'goright':
            toshiba_remote.send_key_command("DPAD_RIGHT")
        elif button_class == 'one':
            toshiba_remote.send_key_command("1")
        elif button_class == 'two':
            toshiba_remote.send_key_command("2")
        elif button_class == 'three':
            toshiba_remote.send_key_command("3")
        elif button_class == 'four':
            toshiba_remote.send_key_command("4")
        elif button_class == 'five':
            toshiba_remote.send_key_command("5")
        elif button_class == 'six':
            toshiba_remote.send_key_command("6")
        elif button_class == 'seven':
            toshiba_remote.send_key_command("7")
        elif button_class == 'eight':
            toshiba_remote.send_key_command("8")
        elif button_class == 'nine':
            toshiba_remote.send_key_command("9")
        elif button_class == 'zero':
            toshiba_remote.send_key_command("0")
        elif button_class == 'f1':
            toshiba_remote.send_key_command("F1")
        elif button_class == 'f2':
            toshiba_remote.send_key_command("F2")
        elif button_class == 'f3':
            toshiba_remote.send_key_command("F3")
        elif button_class == 'f4':
            toshiba_remote.send_key_command("F4")
        elif button_class == 'netflix':
            toshiba_remote.send_launch_app_command("https://www.netflix.com/title")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/panasonic')
def panasonic():
    return render_template("panasonic.html")

@app.route('/panasonic-send-ip', methods=['POST'])
def panasonic_press2():
    global panasonic_remote
    global panasonic_ip
    data = request.get_json()
    panasonicip = data.get('ip')
    if(panasonicip=="no"):
        panasonicip=find_tvs("Panasonic")
    panasonic_ip=panasonicip
    pairing_sock = PairingSocket("hmi", panasonicip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote for Sony TV at key: {panasonicip}'

    return jsonify(response=response_message)

@app.route('/panasonic-button-pressed', methods=['POST'])
def panasonic_button_press():
    global panasonic_remote
    global panasonic_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    panasonic_remote = SendingKeySocket("Panasonic", panasonic_ip)
    panasonic_remote.connect()

    if panasonic_remote:
        if button_class == 'power':
            panasonic_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            panasonic_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            panasonic_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            panasonic_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            panasonic_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            panasonic_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            panasonic_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            panasonic_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            panasonic_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            panasonic_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            panasonic_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            panasonic_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            panasonic_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            panasonic_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            panasonic_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            panasonic_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            panasonic_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            panasonic_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            panasonic_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            panasonic_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            panasonic_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            panasonic_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            panasonic_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            panasonic_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            panasonic_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            panasonic_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            panasonic_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            panasonic_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            panasonic_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            panasonic_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            panasonic_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            panasonic_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)

@app.route('/vizio')
def vizio():
    return render_template("vizio.html")

@app.route('/vizio-send-ip', methods=['POST'])
def vizio_press2():
    global vizio_remote
    global vizio_ip
    data = request.get_json()
    vizioip = data.get('ip')
    if(vizioip=="no"):
        vizioip=find_tvs("VIZIO")
    vizio_ip=vizioip
    pairing_sock = PairingSocket("hmi", vizioip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote for Sony TV at key: {vizioip}'

    return jsonify(response=response_message)

@app.route('/vizio-button-pressed', methods=['POST'])
def vizio_button_press():
    global vizio_remote
    global vizio_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    vizio_remote = SendingKeySocket("VIZIO", vizio_ip)
    vizio_remote.connect()

    if vizio_remote:
        if button_class == 'power':
            vizio_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            vizio_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            vizio_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            vizio_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            vizio_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            vizio_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            vizio_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            vizio_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            vizio_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            vizio_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            vizio_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            vizio_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            vizio_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            vizio_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            vizio_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            vizio_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            vizio_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            vizio_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            vizio_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            vizio_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            vizio_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            vizio_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            vizio_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            vizio_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            vizio_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            vizio_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            vizio_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            vizio_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            vizio_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            vizio_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            vizio_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            vizio_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)

@app.route('/philips')
def philips():
    return render_template("philips.html")


@app.route('/philips-send-ip', methods=['POST'])
def philips_press2():
    global philips_remote
    global philips_ip
    data = request.get_json()
    philipsip = data.get('ip')
    if(philipsip=="no"):
        philipsip=find_tvs("PHILIPS")
    philips_ip=philipsip
    pairing_sock = PairingSocket("hmi", philipsip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote for Sony TV at key: {philipsip}'

    return jsonify(response=response_message)

@app.route('/philips-button-pressed', methods=['POST'])
def philips_button_press():
    global philips_remote
    global philips_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    philips_remote = SendingKeySocket("PHILIPS", philips_ip)
    philips_remote.connect()

    if philips_remote:
        if button_class == 'power':
            philips_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            philips_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            philips_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            philips_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            philips_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            philips_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            philips_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            philips_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            philips_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            philips_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            philips_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            philips_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            philips_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            philips_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            philips_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            philips_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            philips_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            philips_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            philips_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            philips_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            philips_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            philips_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            philips_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            philips_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            philips_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            philips_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            philips_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            philips_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            philips_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            philips_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            philips_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            philips_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/thomson')
def thomson():
    return render_template("thomson.html")

@app.route('/thomson-send-ip', methods=['POST'])
def thomson_press2():
    global thomson_remote
    global thomson_ip
    data = request.get_json()
    thomsonip = data.get('ip')
    if(thomsonip=="no"):
        thomsonip=find_tvs("THOMSON")
    thomson_ip=thomsonip
    pairing_sock = PairingSocket("hmi", thomsonip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote'

    return jsonify(response=response_message)


@app.route('/thomson-button-pressed', methods=['POST'])
def thomson_button_press():
    global thomson_remote
    global thomson_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    thomson_remote = SendingKeySocket("THOMSON", thomson_ip)
    thomson_remote.connect()

    if thomson_remote:
        if button_class == 'power':
            thomson_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            thomson_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            thomson_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            thomson_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            thomson_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            thomson_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            thomson_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            thomson_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            thomson_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            thomson_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            thomson_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            thomson_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            thomson_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            thomson_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            thomson_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            thomson_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            thomson_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            thomson_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            thomson_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            thomson_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            thomson_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            thomson_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            thomson_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            thomson_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            thomson_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            thomson_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            thomson_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            thomson_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            thomson_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            thomson_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            thomson_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            thomson_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/aconatic')
def aconatic():
    return render_template("aconatic.html")

@app.route('/aconatic-send-ip', methods=['POST'])
def aconatic_press2():
    global aconatic_remote
    global aconatic_ip
    data = request.get_json()
    aconaticip = data.get('ip')
    if(aconaticip=="no"):
        aconaticip=find_tvs("Aconatic")
    aconatic_ip=aconaticip
    pairing_sock = PairingSocket("hmi", aconaticip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote'

    return jsonify(response=response_message)

@app.route('/aconatic-button-pressed', methods=['POST'])
def aconatic_button_press():
    global aconatic_remote
    global aconatic_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    aconatic_remote = SendingKeySocket("Aconatic", aconatic_ip)
    aconatic_remote.connect()

    if aconatic_remote:
        if button_class == 'power':
            aconatic_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            aconatic_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            aconatic_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            aconatic_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            aconatic_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            aconatic_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            aconatic_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            aconatic_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            aconatic_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            aconatic_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            aconatic_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            aconatic_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            aconatic_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            aconatic_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            aconatic_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            aconatic_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            aconatic_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            aconatic_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            aconatic_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            aconatic_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            aconatic_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            aconatic_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            aconatic_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            aconatic_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            aconatic_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            aconatic_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            aconatic_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            aconatic_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            aconatic_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            aconatic_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            aconatic_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            aconatic_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/asus')
def asus():
    return render_template("asus.html")

@app.route('/asus-send-ip', methods=['POST'])
def asus_press2():
    global asus_remote
    global asus_ip
    data = request.get_json()
    asusip = data.get('ip')
    if(asusip=="no"):
        asusip=find_tvs("ASUS")
    asus_ip=asusip
    pairing_sock = PairingSocket("hmi", asusip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote'

    return jsonify(response=response_message)



@app.route('/asus-button-pressed', methods=['POST'])
def asus_button_press():
    global asus_remote
    global asus_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    asus_remote = SendingKeySocket("ASUS", asus_ip)
    asus_remote.connect()

    if asus_remote:
        if button_class == 'power':
            asus_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            asus_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            asus_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            asus_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            asus_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            asus_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            asus_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            asus_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            asus_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            asus_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            asus_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            asus_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            asus_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            asus_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            asus_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            asus_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            asus_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            asus_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            asus_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            asus_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            asus_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            asus_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            asus_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            asus_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            asus_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            asus_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            asus_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            asus_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            asus_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            asus_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            asus_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            asus_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/asanzo')
def asanzo():
    return render_template("asanzo.html")

@app.route('/asanzo-send-ip', methods=['POST'])
def asanzo_press2():
    global asanzo_remote
    global asanzo_ip
    data = request.get_json()
    asanzoip = data.get('ip')
    if(asanzoip=="no"):
        asanzoip=find_tvs("ASANZO")
    asanzo_ip=asanzoip
    pairing_sock = PairingSocket("hmi", asanzoip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote'

    return jsonify(response=response_message)

@app.route('/asanzo-button-pressed', methods=['POST'])
def asanzo_button_press():
    global asanzo_remote
    global asanzo_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    asanzo_remote = SendingKeySocket("ASANZO", asanzo_ip)
    asanzo_remote.connect()

    if asanzo_remote:
        if button_class == 'power':
            asanzo_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            asanzo_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            asanzo_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            asanzo_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            asanzo_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            asanzo_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            asanzo_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            asanzo_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            asanzo_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            asanzo_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            asanzo_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            asanzo_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            asanzo_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            asanzo_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            asanzo_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            asanzo_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            asanzo_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            asanzo_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            asanzo_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            asanzo_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            asanzo_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            asanzo_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            asanzo_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            asanzo_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            asanzo_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            asanzo_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            asanzo_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            asanzo_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            asanzo_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            asanzo_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            asanzo_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            asanzo_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/casper')
def casper():
    return render_template("casper.html")

@app.route('/casper-send-ip', methods=['POST'])
def casper_press2():
    global casper_remote
    global casper_ip
    data = request.get_json()
    casperip = data.get('ip')
    if(casperip=="no"):
        casperip=find_tvs("Casper")
    casper_ip=casperip
    pairing_sock = PairingSocket("hmi", casperip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote'

    return jsonify(response=response_message)

@app.route('/casper-button-pressed', methods=['POST'])
def casper_button_press():
    global casper_remote
    global casper_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    casper_remote = SendingKeySocket("Casper", casper_ip)
    casper_remote.connect()

    if casper_remote:
        if button_class == 'power':
            casper_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            casper_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            casper_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            casper_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            casper_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            casper_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            casper_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            casper_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            casper_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            casper_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            casper_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            casper_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            casper_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            casper_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            casper_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            casper_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            casper_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            casper_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            casper_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            casper_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            casper_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            casper_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            casper_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            casper_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            casper_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            casper_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            casper_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            casper_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            casper_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            casper_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            casper_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            casper_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)


@app.route('/tclandroid')
def tclandroid():
    return render_template("tclandroid.html")

@app.route('/tclandroid-send-ip', methods=['POST'])
def tclandroid_press2():
    global tclandroid_remote
    global tclandroid_ip
    data = request.get_json()
    tclandroidip = data.get('ip')
    if(tclandroidip=="no"):
        tclandroidip=find_tvs("TCL")
    tclandroid_ip=tclandroidip
    pairing_sock = PairingSocket("hmi", tclandroidip)
    pairing_sock.connect()
    pairing_sock.start_pairing()
    assert (pairing_sock.connected),"Connection unsuccessful!"

    response_message = f'Successfully configured remote'

    return jsonify(response=response_message)


@app.route('/tclandroid-button-pressed', methods=['POST'])
def tclandroid_button_press():
    global tclandroid_remote
    global tclandroid_ip
    data = request.get_json()
    button_class = data.get('buttonClass')
    tclandroid_remote = SendingKeySocket("TCL", tclandroid_ip)
    tclandroid_remote.connect()

    if tclandroid_remote:
        if button_class == 'power':
            tclandroid_remote.send_key_command(KEYCODE_POWER)
        elif button_class == 'home':
            tclandroid_remote.send_key_command(KEYCODE_HOME)
        elif button_class == 'back':
            tclandroid_remote.send_key_command(KEYCODE_BACK)
        elif button_class == 'info':
            tclandroid_remote.send_key_command(KEYCODE_INFO)
        elif button_class == 'tools':
            tclandroid_remote.send_key_command(KEYCODE_EXPLORER)
        elif button_class == 'guide':
            tclandroid_remote.send_key_command(KEYCODE_GUIDE)
        elif button_class == 'menu':
            tclandroid_remote.send_key_command(KEYCODE_MENU)
        elif button_class == 'mute':
            tclandroid_remote.send_key_command(KEYCODE_MUTE)
        elif button_class == 'volumeup':
            tclandroid_remote.send_key_command(KEYCODE_VOLUME_UP)
        elif button_class == 'volumedown':
            tclandroid_remote.send_key_command(KEYCODE_VOLUME_DOWN)
        elif button_class == 'channelup':
            tclandroid_remote.send_key_command(KEYCODE_CHANNEL_UP)
        elif button_class == 'channeldown':
            tclandroid_remote.send_key_command(KEYCODE_CHANNEL_DOWN)
        elif button_class == 'enter':
            tclandroid_remote.send_key_command(KEYCODE_ENTER)
        elif button_class == 'goup':
            tclandroid_remote.send_key_command(KEYCODE_DPAD_UP)
        elif button_class == 'godown':
            tclandroid_remote.send_key_command(KEYCODE_DPAD_DOWN)
        elif button_class == 'goleft':
            tclandroid_remote.send_key_command(KEYCODE_DPAD_LEFT)
        elif button_class == 'goright':
            tclandroid_remote.send_key_command(KEYCODE_DPAD_RIGHT)
        elif button_class == 'one':
            tclandroid_remote.send_key_command(KEYCODE_1)
        elif button_class == 'two':
            tclandroid_remote.send_key_command(KEYCODE_2)
        elif button_class == 'three':
            tclandroid_remote.send_key_command(KEYCODE_3)
        elif button_class == 'four':
            tclandroid_remote.send_key_command(KEYCODE_4)
        elif button_class == 'five':
            tclandroid_remote.send_key_command(KEYCODE_5)
        elif button_class == 'six':
            tclandroid_remote.send_key_command(KEYCODE_6)
        elif button_class == 'seven':
            tclandroid_remote.send_key_command(KEYCODE_7)
        elif button_class == 'eight':
            tclandroid_remote.send_key_command(KEYCODE_8)
        elif button_class == 'nine':
            tclandroid_remote.send_key_command(KEYCODE_9)
        elif button_class == 'zero':
            tclandroid_remote.send_key_command(KEYCODE_0)
        elif button_class == 'f1':
            tclandroid_remote.send_key_command(KEYCODE_F1)
        elif button_class == 'f2':
            tclandroid_remote.send_key_command(KEYCODE_F2)
        elif button_class == 'f3':
            tclandroid_remote.send_key_command(KEYCODE_F3)
        elif button_class == 'f4':
            tclandroid_remote.send_key_command(KEYCODE_F4)
        elif button_class == 'netflix':
            tclandroid_remote.send_lunch_app_command("netflix")

        response_message = f'Successfully sent {button_class} command'
    else:
        response_message = 'Please configure the remote first'

    return jsonify(response=response_message)



if __name__ == '__main__':
    app.run(debug=True)
