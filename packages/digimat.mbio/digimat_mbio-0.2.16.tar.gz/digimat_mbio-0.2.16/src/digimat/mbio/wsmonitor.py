import importlib_resources
import json
from .task import MBIOTask
from .xmlconfig import XMLConfig

from .wserver import TemporaryWebServer

class Html():
    def __init__(self, title=None, handler=None):
        self._handler=handler
        self._header=''
        self._body=''
        self._variables={}
        self.onInit()

        if title:
            self.header(f'<title>{title}</title>')

    def onInit(self):
        pass

    def header(self, data):
        if data:
            self._header+=data
            self._header+='\n'

    def style(self, data):
        if data:
            self.header(f'<style>{data}</style>')

    def variable(self, name, value):
        if name:
            name='{%s}' % name.lower()
            if value is None:
                value=''
            value=str(value)
            self._variables[name]=value

    def body(self, data):
        if data:
            if self._variables:
                for v in self._variables.keys():
                    data=data.replace(v, self._variables[v])
            self._body+=data
            self._body+='\n'

    def readFile(self, fname):
        try:
            my_resources = importlib_resources.files("digimat.mbio")
            data = my_resources.joinpath(fname).read_text()
            self.write(data)
            return True
        except:
            pass
        return False

    def write(self, data):
        self.body(data)

    def data(self):
        if self._header:
            data='<html>'
            data+='<head>'
            data+=self._header
            data+='</head>'
            data+='<body>'
            data+=self._body
            data+='</body>'
            data+='</html>'
        else:
            data=self._body
        return data

    def bytes(self):
        return self.data().encode('utf-8')

    def flush(self):
        handler=self._handler
        if handler:
            handler.send_response(200)
            handler.send_header("Content-Type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(self.bytes())

    def button(self, bid, name):
        self.write(f'<button id="{bid}" class="ui-button red-button ui-widget ui-corner-all">{name}</button>')


class HtmlPage(Html):
    def onInit(self):
        super().onInit()

        self.header('<meta charset="utf-8" />')
        self.header('<meta name="viewport" content="width=device-width, initial-scale=1" />')

        # self.header('<link rel="stylesheet" href="/www/jquery-ui/jquery-ui.min.css">')
        # self.header('<script src="/www/jquery-ui/external/jquery/jquery.js"></script>')
        # self.header('<script src="/www/jquery-ui/jquery-ui.min.js"></script>')

        # https://jquery.com/download/
        self.body('<script src="/www/jquery/jquery.min.js"></script>')

        # https://getbootstrap.com/docs/5.0/getting-started/download/
        self.header('<link href="/www/Bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">')
        self.body('<script src="/www/Bootstrap/dist/js/bootstrap.bundle.min.js"></script>')

        # https://datatables.net/download/
        self.header('<link href="/www/DataTables/datatables.min.css" rel="stylesheet">')
        self.body('<script src="/www/DataTables/datatables.min.js"></script>')

        self.style('.red-button {background-color: red; color: white;}')

        data="""
        .form-switch {
        position: relative;
        display: inline-block;
        width: 42px;
        height: 22px;
        }

        .form-switch input {
        opacity: 0;
        width: 0;
        height: 0;
        }

        .form-switch .slider {
        position: absolute;
        cursor: pointer;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #ccc;
        border-radius: 22px;
        transition: .3s;
        }

        .form-switch .slider:before {
        position: absolute;
        content: "";
        height: 18px; width: 18px;
        left: 2px; bottom: 2px;
        background-color: white;
        border-radius: 50%;
        transition: .3s;
        }

        .form-switch input:checked + .slider {
        background-color: #4caf50;
        }

        .form-switch input:checked + .slider:before {
        transform: translateX(20px);
        }

        @keyframes flashRow { 0%{background:#fff3cd;} 100%{background:white;} }
        .flash-update { animation: flashRow 1.2s ease-out 1; }
        """
        self.style(data)

    def header(self, data):
        if data:
            self._header+=data
            self._header+='\n'

    def style(self, data):
        if data:
            self.header(f'<style>{data}</style>')

    def variable(self, name, value):
        if name:
            name='{%s}' % name.lower()
            if value is None:
                value=''
            value=str(value)
            self._variables[name]=value

    def body(self, data):
        if data:
            if self._variables:
                for v in self._variables.keys():
                    data=data.replace(v, self._variables[v])
            self._body+=data
            self._body+='\n'

    def write(self, data):
        self.body(data)

    def data(self):
        data='<html>'
        data+='<head>'
        data+=self._header
        data+='</head>'
        data+='<body>'
        data+=self._body
        data+='</body>'
        data+='</html>'
        return data

    def bytes(self):
        return self.data().encode('utf-8')

    def flush(self):
        handler=self._handler
        if handler:
            handler.send_response(200)
            handler.send_header("Content-Type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(self.bytes())

    def button(self, bid, name):
        self.write(f'<button id="{bid}" class="ui-button red-button ui-widget ui-corner-all">{name}</button>')


class MBIOWsMonitor(MBIOTask):
    def initName(self):
        return 'wsmon'

    @property
    def wserver(self) -> TemporaryWebServer:
        return self._wserver

    def readLocalFileContent(self, fname):
        try:
            my_resources = importlib_resources.files("digimat.mbio")
            data = my_resources.joinpath(fname).read_bytes()
            return data
        except:
            pass

    def onInit(self):
        self._wserver=None

    def cb_headers_html(self, handler, rcode=200):
        handler.send_response(rcode)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.end_headers()

    def cb_headers_json(self, handler, rcode=200):
        handler.send_response(rcode)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Access-Control-Allow-Origin", '*') # CORS pour dev
        handler.end_headers()

    def cb_write_json(self, handler, data, rcode=200):
        self.cb_headers_json(handler, rcode)
        data=json.dumps(data)
        handler.wfile.write(data.encode('utf-8'))

    def cb_write_success(self, handler):
        data={'success': True}
        return self.cb_write_json(handler, data)

    def cb_write_failure(self, handler):
        data={'success': False}
        return self.cb_write_json(handler, data, 400)

    def cb_storeuserdata(self, handler, params, data=None):
        """Store data given by it's name to the internal storage system"""

        key=params.get('key')
        value=params.get('value') or data

        # self.logger.warning(key)
        # self.logger.warning(value)

        try:
            if key and value:
                name='%s.userdata' % key
                self.pickleWrite(name, value)
                self.cb_write_success(handler)
                return True
        except:
            pass
        self.cb_write_failure(handler)

    def cb_getuserdata(self, handler, params):
        """Retrieve stored data given by it's name from the internal storage system"""

        key=params.get('key')

        try:
            if key:
                name='%s.userdata' % key
                value=self.pickleRead(name)
                if isinstance(value, dict):
                    data=value
                else:
                    data={}
                    data[key]=value

                self.cb_write_json(handler, data)
                return True
        except:
            pass
        self.cb_write_failure(handler)

    def cb_gettasks(self, handler, params):
        """Retrieve all knwown tasks"""

        mbio=self.getMBIO()
        items=[]
        for t in mbio.tasks.all():
            item={'key': t.key}
            item['class']=t.__class__.__name__
            item['state']=t.statestr(),
            item['statetime']=int(t.statetime())
            item['error']=t.isError()
            item['countvalues']=t.values.count()
            items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_resettask(self, handler, params):
        """Trigger a MBIO state reset for the given task"""

        mbio=self.getMBIO()
        key=params.get('key')
        t=mbio.task(key)
        if t:
            t.reset()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_resetgateway(self, handler, params):
        """Trigger a MBIO state reset for the given gateway"""

        mbio=self.getMBIO()
        key=params.get('key')
        g=mbio.gateway(key)
        if g:
            g.reset()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_resetdevice(self, handler, params):
        """Trigger a MBIO state reset for the given device"""

        mbio=self.getMBIO()
        key=params.get('key')
        d=mbio.device(key)
        if d:
            d.reset()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_rebootdevice(self, handler, params):
        """Trigger a reboot for the given device"""

        mbio=self.getMBIO()
        key=params.get('key')
        d=mbio.device(key)
        if d:
            d.reboot()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_upgradedevice(self, handler, params):
        """Trigger a firmware upgrade for the given device"""

        mbio=self.getMBIO()
        d=mbio.device(key)
        if d:
            d.upgrade()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_beep(self, handler, params):
        """Beep the MBIO processor"""

        mbio=self.getMBIO()
        mbio.beep()
        self.cb_write_success(handler)
        return True

    def cb_save(self, handler, params):
        """Order a data save"""

        mbio=self.getMBIO()
        mbio.storeKeyToZoneInformation(True)
        self.cb_write_success(handler)
        return True

    def cb_setvalue(self, handler, params):
        """Set the given MBIO value to manual"""

        mbio=self.getMBIO()
        key=params.get('key')
        v=params.get('value')
        value=mbio.value(key)
        if value is not None:
            if v=="auto":
                value.auto()
            else:
                value.manual(v)
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_setvalueauto(self, handler, params):
        """Set the given MBIO value to automatic"""

        mbio=self.getMBIO()
        key=params.get('key')
        value=mbio.value(key)
        if value is not None:
            value.auto()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_markvalue(self, handler, params):
        """Mark the given MBIO value"""

        mbio=self.getMBIO()
        key=params.get('key')
        value=mbio.value(key)
        if value is not None:
            value.mark()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_markvaluewithzone(self, handler, params):
        """Mark the MBIO value with corresponding zone"""

        mbio=self.getMBIO()
        zone=params.get('zone')
        if zone:
            mbio.markValuesWithZone(zone)
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_unmarkvalue(self, handler, params):
        """Unmark the given MBIO value"""

        mbio=self.getMBIO()
        key=params.get('key')
        value=mbio.value(key)
        if value is not None:
            value.unmark()
            self.cb_write_success(handler)
            return True
        self.cb_write_failure(handler)

    def cb_getzones(self, handler, params):
        """Retrieve all known zones"""

        mbio=self.getMBIO()
        items=[]

        for zone in mbio.zones():
            item={'zone': zone.lower()}
            values=mbio.valuesWithZone(zone)
            error=False

            for v in values:
                if v.isError():
                    error=True
                    break

            item['error']=error
            item['#values']=len(values)
            items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_setzone(self, handler, params, data=None):
        """Change the zone of the given value/device"""
        mbio=self.getMBIO()

        zone=params.get('zone')
        if zone in ['none', 'null', '']:
            zone=None
        key=params.get('key')

        if key:
            value=mbio.value(key)
            if value is not None:
                value.setZone(zone)
                self.cb_write_success(handler)
                return True

            device=mbio.device(key)
            if device is not None:
                device.setZone(zone)
                self.cb_write_success(handler)
                return True

        if data:
            # self.logger.warning(data)
            # { 'key' : 'zname' }
            for key in data.keys():
                zone=data[key]

                value=mbio.value(key)
                if value is not None:
                    value.setZone(zone)
                else:
                    device=mbio.device(key)
                    if device is not None:
                        device.setZone(zone)
            self.cb_write_success(handler)
            return True

        self.cb_write_failure(handler)

    def cb_getgateways(self, handler, params):
        """Retrieve all known gateways"""

        mbio=self.getMBIO()
        items=[]

        for g in mbio.gateways.all():
            item={'key': g.key, 'name': g.name,
                  'host': g.host, 'mac': g.MAC,
                  'model': g.model}
            item['class']=g.__class__.__name__
            state='CLOSED'
            if g.isOpen():
                state='OPEN'
            item['state']=state
            item['error']=g.isError()
            item['countdevices']=g.devices.count()
            item['zone']=g.zone
            items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getgatewaydevices(self, handler, params):
        """Retrieve all devices of a given gateway"""

        mbio=self.getMBIO()
        g=mbio.gateway(params.get('gateway'))

        items=[]
        if g is not None:
            for d in g.devices.all():
                self.microsleep()
                item={'gateway': g.key, 'address': d.address,
                      'key': d.key, 'vendor': d.vendor,
                      'model': d.model, 'state': d.statestr()}
                item['class']=d.__class__.__name__
                item['version']=None
                if d.version and d.firmware:
                    item['version']=f'{d.version}/{d.firmware}'
                elif d.version:
                    item['version']=d.version
                else:
                    item['version']=d.firmware

                item['statetime']=int(d.statetime())
                item['countmsg']=d.countMsg
                item['countmsgerr']=d.countMsgErr
                item['error']=d.isError()
                item['countvalues']=d.values.count()
                item['ismanualvalue']=d.isManualValue()
                item['countvalues']=d.values.count()
                item['reboot']=d.isRebootPossible()
                item['upgrade']=d.isUpgradePossible()
                item['zone']=d.zone
                items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getalldevices(self, handler, params):
        """Retrieve all known devices"""

        mbio=self.getMBIO()
        items=[]
        for g in mbio.gateways.all():
            if g is not None:
                for d in g.devices.all():
                    self.microsleep()
                    item={'gateway': g.key, 'address': d.address,
                          'key': d.key, 'vendor': d.vendor,
                          'model': d.model, 'state': d.statestr()}
                    item['class']=d.__class__.__name__
                    item['version']=None
                    if d.version and d.firmware:
                        item['version']=f'{d.version}/{d.firmware}'
                    elif d.version:
                        item['version']=d.version
                    else:
                        item['version']=d.firmware

                    item['statetime']=int(d.statetime())
                    item['countmsg']=d.countMsg
                    item['countmsgerr']=d.countMsgErr
                    item['error']=d.isError()
                    item['countvalues']=d.values.count()
                    item['ismanualvalue']=d.isManualValue()
                    item['countvalues']=d.values.count()
                    item['reboot']=d.isRebootPossible()
                    item['upgrade']=d.isUpgradePossible()
                    item['zone']=d.zone
                    items.append(item)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def addValueItemToDataResponse(self, items, value):
        if value is not None and value.isEnabled():
            item={'key': value.key, 'value': value.value, 'toreachvalue': None,
                    'valuestr': value.valuestr(),
                    'unit': value.unit, 'unitstr': value.unitstr(),
                    'flags': value.flags, 'age': int(value.age()), 'tag': value.tag}
            if value.isWritable():
                item['toreachvalue']=value.toReachValue
            item['class']=value.__class__.__name__
            item['error']=value.isError()
            item['writable']=value.isWritable()
            item['digital']=value.isDigital()
            item['enable']=value.isEnabled()
            item['manual']=value.isManual()
            item['marked']=value.isMarked()
            item['notifycount']=value.notifyCount
            item['description']=value.description
            item['zone']=value.zone
            item['parent']=None
            try:
                item['parent']=value.parent.parent.key
            except:
                pass
            item['zoneparent']=value.zoneParent
            items.append(item)
            # self.microsleep()
        return items

    def cb_gettaskvalues(self, handler, params):
        """Retrieve MBIO values for a given task"""

        mbio=self.getMBIO()
        t=mbio.task(params.get('task'))

        items=[]
        if t is not None:
            for v in t.values.all():
                self.addValueItemToDataResponse(items, v)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getzonevalues(self, handler, params):
        """Retrieve MBIO values associeted to the given zone"""

        mbio=self.getMBIO()
        zone=params.get('zone')

        items=[]
        if zone is not None:
            for v in mbio.valuesWithZone(zone):
                self.addValueItemToDataResponse(items, v)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getdevicevalues(self, handler, params):
        """Retrieve MBIO values for a given device"""

        mbio=self.getMBIO()

        key=params.get('device')

        items=[]
        if key is not None:
            if ',' in key:
                keys=key.split(',')
                for key in keys:
                    d=mbio.device(key)
                    if d is not None:
                        for v in d.values.all():
                            self.addValueItemToDataResponse(items, v)
            else:
                d=mbio.device(key)
                for v in d.values.all():
                    self.addValueItemToDataResponse(items, v)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_getvalues(self, handler, params):
        """Retrieve MBIO values"""

        mbio=self.getMBIO()

        key=params.get('key')
        manual=params.get('manual')
        error=params.get('error')
        marked=params.get('marked')

        values=[]
        if key:
            if ',' in key:
                keys=key.split(',')
                for key in keys:
                    v=mbio.value(key)
                    if v is not None:
                        values.append(v)
            else:
                v=mbio.value(key)
                if v is not None:
                    values.append(v)
        else:
            values=mbio.values(params.get('filter'))

        if manual:
            values=[v for v in values if v.isManual()]
        if error:
            values=[v for v in values if v.isError()]
        if marked:
            values=[v for v in values if v.isMarked()]

        items=[]
        for v in values:
            self.addValueItemToDataResponse(items, v)

        data={'data': items}
        self.cb_write_json(handler, data)
        return True

    def cb_tasks(self, handler, params):
        """Present an html page with all known tasks"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><b>Tasks</b></p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/gateways">Gateways</a> /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/values">Values</a> /
                    <a href="/valuesmarked">Marks</a> /
                    <a href="/zones">Zones</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>State</th>
                            <th>Age</th>
                            <th>Error</th>
                            <th>#Values</th>
                            <th>Class</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        h.write(data)

        data="""
        <script>
            $(function () {
                const table = new DataTable('#items', {
                responsive: true,
                paging: false,
                searching: true,
                ordering: true,
                info: false,
                search: {
                    smart: true,
                    regex: false,
                    caseInsensitive: true,
                    boundary: false
                },
                ajax: {
                    url: "/api/v1/gettasks",
                    dataSrc: "data"
                },
                columns: [
                    { data: "key" },
                    { data: "state",
                        render: function (data, type, row) {
                            if (type !== "display") return data;
                            return `<div class="d-flex justify-content-between align-items-center">
                                <span>${data}</span>
                                <button class="btn btn-sm btn-outline-secondary cell-action" data-id="${row.key}">
                                    Reset
                                </button>
                                </div>`;
                            }
                    },
                    { data: "statetime" },
                    { data: "error", render: v=>v ? 'ERR' : 'OK' },
                    { data: "countvalues" },
                    { data: "class" }
                ],
                rowCallback: function (row, data) {
                    if (data.error) {
                        $('td', row).css('background-color', 'pink');
                    }
                }
                });

                $("#items tbody").on("click", ".cell-action, .action-btn", async function (e) {
                    e.stopPropagation();
                    const row = table.row(this.closest('tr'));
                    const data = row.data();
                    try {
                        const r = await fetch(`/api/v1/resettask?key=${data.key}`, {method: "GET"});
                    } catch (err) {
                    }
                });

                $('#items').on('click','tr', function(e) {
                    var $clickedCell = $(e.target).closest('td');
                    if ($clickedCell.length) {
                        var columnIndex = $clickedCell.index();
                        if (columnIndex !== 0) {
                            var data = table.row(this).data();
                            const url = "/taskvalues?task=" + encodeURIComponent(data.key);
                            window.location.href = url;
                        }
                    }
                });

                setInterval(function () {
                    table.ajax.reload(null, false);
                    }, 2000);

            });
        </script>
        """
        h.write(data)
        h.flush()

    def cb_zones(self, handler, params):
        """Present an html page with all known zones"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><b>Zones [<a href='/zoneeditor'>EDIT</a>]</b></p>
                    </div>
                    <div class="text-muted small">{mbio.version}</b>
                    <a href="/gateways">Gateways</a> /
                    <a href="/devices">Devices</a> /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/tasks">Tasks</a> /
                    <a href="/valuesmarked">Marks</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th>Zone</th>
                            <th>Values</th>
                            <th>Error</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        h.write(data)

        data="""
        <script>
            $(function () {
                const table = new DataTable('#items', {
                responsive: true,
                paging: false,
                searching: true,
                ordering: true,
                info: false,
                search: {
                    smart: true,
                    regex: false,
                    caseInsensitive: true,
                    boundary: false
                },
                ajax: {
                    url: "/api/v1/getzones",
                    dataSrc: "data"
                },
                columns: [
                    { data: "zone" },
                    { data: "#values" },
                    { data: "error", render: v=>v ? 'ERR' : 'OK' }
                ],
                rowCallback: function (row, data) {
                    if (data.error) {
                        $('td', row).css('background-color', 'pink');
                    }
                }

                });

                $('#items').on('click','tr', function(e) {
                    var $clickedCell = $(e.target).closest('td');
                    if ($clickedCell.length) {
                        var data = table.row(this).data();
                        const url = "/zonevalues?zone=" + encodeURIComponent(data.zone);
                        window.location.href = url;
                    }
                });

                /*
                setInterval(function () {
                    table.ajax.reload(null, false);
                    }, 10000);
                */

            });
        </script>
        """
        h.write(data)
        h.flush()

    def cb_gateways(self, handler, params):
        """Present an html page with all known gateways"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><b>Gateways</b></p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/tasks">Tasks</a> /
                    <a href="/values">Values</a> /
                    <a href="/valuesmarked">Marks</a> /
                    <a href="/zones">Zones</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Host</th>
                            <th data-priority="2">MAC</th>
                            <th data-priority="1">State</th>
                            <th data-priority="4">Error</th>
                            <th data-priority="5">#Devices</th>
                            <th data-priority="2">Class</th>
                            <th data-priority="3">Zone</th>
                        </tr>
                    </thead>
                    </table>
                </div>
            </div>
        """
        h.write(data)

        data="""
        <script>
            $(function () {
                const table = new DataTable('#items', {
                responsive: true,
                paging: false,
                searching: true,
                ordering: true,
                info: false,
                search: {
                    smart: true,
                    regex: false,
                    caseInsensitive: true,
                    boundary: false
                },
                ajax: {
                    url: "/api/v1/getgateways",
                    dataSrc: "data"
                },
                columns: [
                    { data: "key" },
                    { data: "host" },
                    { data: "mac" },
                    { data: "state",
                        render: function (data, type, row) {
                            if (type !== "display") return data;
                            return `<div class="d-flex justify-content-between align-items-center">
                                <span>${data}</span>
                                <button class="btn btn-sm btn-outline-secondary cell-action" data-id="${row.key}">
                                    Reset
                                </button>
                                </div>`;
                            }
                    },
                    { data: "error", render: v=>v ? 'ERR' : 'OK' },
                    { data: "countdevices" },
                    { data: "class" },
                    { data: "zone" }
                ],
                rowCallback: function (row, data) {
                    if (data.error) {
                        $('td', row).css('background-color', 'pink');
                    }
                }
                });

                $("#items tbody").on("click", ".cell-action, .action-btn", async function (e) {
                    e.stopPropagation();
                    const row = table.row(this.closest('tr'));
                    const data = row.data();
                    try {
                        const r = await fetch(`/api/v1/resetgateway?key=${data.key}`, {method: "GET"});
                    } catch (err) {
                    }
                });

                $('#items').on('click','tr', function(e) {
                    var $clickedCell = $(e.target).closest('td');
                    if ($clickedCell.length) {
                        var columnIndex = $clickedCell.index();
                        if (columnIndex !== 0) {
                            var data = table.row(this).data();
                            const url = "/devices?gateway=" + encodeURIComponent(data.key);
                            window.location.href = url;
                        }
                    }
                });

                $(document).on('keydown', function (e) {
                    if ($(e.target).is('input, textarea')) return;

                    if (!e.ctrlKey && !e.metaKey && !e.altKey && e.key === '/') {
                        e.preventDefault();
                        const searchInput = $('#dt-search-0.dt-input');
                        searchInput.focus();
                        searchInput.select();
                    }
                });

                setInterval(function () {
                    table.ajax.reload(null, false);
                    }, 2000);

            });
        </script>
        """
        h.write(data)
        h.flush()

    def cb_devices(self, handler, params):
        """Present an html page with all devices of a given gateway"""

        gateway=params.get('gateway')

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)
        h.variable('gateway', gateway)

        data="""
            <div class="page container-fluid">
            <div class="card p-4 p-lg-5">
            <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
            <div>
            <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
            <p class="text-secondary mb-0"><a href="/gateways">Gateways</a> / <b>{gateway}</b> / devices</p>
            </div>
            <div class="text-muted small">{mbio.version} /
            <a href="/alldevices">*Devices</a> /
            <a href="/tasks">Tasks</a> /
            <a href="/values">Values</a> /
            <a href="/valuesmarked">Marks</a> /
            <a href="/zones">Zones</a>
            </div>
            </div>
            <table id="items" class="display nowrap" style="width:100%">
            <thead>
            <tr>
            <th data-priority="1">Address</th>
            <th data-priority="1">Key</th>
            <th data-priority="2">Vendor</th>
            <th data-priority="2">Model</th>
            <th data-priority="2">Version</th>
            <th data-priority="4">Upgrade</th>
            <th data-priority="1">State</th>
            <th data-priority="6">Age</th>
            <th data-priority="8">Error</th>
            <th data-priority="9">#Values</th>
            <th data-priority="10">#Msg</th>
            <th data-priority="10">#MsgErr</th>
            <th data-priority="2">Class</th>
            <th data-priority="1">Zone</th>
            <th data-priority="4">Reboot</th>
            </tr>
            </thead>
            </table>
            </div>
            </div>
        """
        h.write(data)

        data="""
        <script>
            $(function () {
            const table = new DataTable('#items', {
            responsive: true,
            paging: false,
            searching: true,
            ordering: true,
            info: false,
            search: {
                smart: true,
                regex: false,
                caseInsensitive: true,
                boundary: false
            },
            ajax: {
                url: "/api/v1/getgatewaydevices?gateway={gateway}",
                dataSrc: "data"
            },
            columns: [
                { data: "address" },
                { data: "key" },
                { data: "vendor" },
                { data: "model" },
                { data: "version" },
                { data: "upgrade",
                    render: function (data, type, row) {
                        if (type !== "display") return data;
                        if (row.upgrade && !row.error) {
                            return `<div class="d-flex justify-content-between align-items-center">
                                    <button class="btn btn-sm btn-outline-secondary cell-action"
                                        data-field="upgrade" data-id="${row.key}">
                                    Upgrade
                                    </button>
                                    </div>`;
                        }
                        return '';
                    }
                },
                { data: "state",
                    render: function (data, type, row) {
                        if (type !== "display") return data;
                        return `<div class="d-flex justify-content-between align-items-center">
                            <span>${data}</span>
                            <button class="btn btn-sm btn-outline-secondary cell-action"
                                data-field="state" data-id="${row.key}">
                                Reset
                            </button>
                            </div>`;
                        }
                },
                { data: "statetime" },
                { data: "error", render: v=>v ? 'ERR' : 'OK' },
                { data: "countvalues" },
                { data: "countmsg" },
                { data: "countmsgerr" },
                { data: "class" },
                { data: "zone" },
                { data: "reboot",
                    render: function (data, type, row) {
                        if (type !== "display") return data;
                        if (row.reboot && !row.error) {
                            return `<div class="d-flex justify-content-between align-items-center">
                                    <button class="btn btn-sm btn-outline-secondary cell-action"
                                        data-field="reboot" data-id="${row.key}">
                                    Reboot
                                    </button>
                                    </div>`;
                        }
                        return '';
                    }
                }
            ],
            rowCallback: function (row, data) {
                if (data.error) {
                    $('td', row).css('background-color', 'pink');
                }
            }
            });

            setInterval(function () {
                table.ajax.reload(null, false);
                }, 2000);

            $("#items tbody").on("click", ".cell-action, .action-btn", async function (e) {
                e.stopPropagation();

                const $ui = $(this);
                const $tr    = $ui.closest('tr');
                const colKey = $ui.data('field');
                const rowApi = table.row($tr);
                const row    = rowApi.data();

                if (colKey=='state') {
                    try {
                        const r = await fetch(`/api/v1/resetdevice?key=${row.key}`, {method: "GET"});
                    } catch (err) {
                    }
                } else if (colKey=='reboot') {
                    try {
                        const r = await fetch(`/api/v1/rebootdevice?key=${row.key}`, {method: "GET"});
                    } catch (err) {
                    }
                } else if (colKey=='upgrade') {
                    try {
                        const r = await fetch(`/api/v1/upgradedevice?key=${row.key}`, {method: "GET"});
                    } catch (err) {
                    }
                }
            });

            $('#items').on('click','tr', function(e) {
                var $clickedCell = $(e.target).closest('td');
                if ($clickedCell.length) {
                    var columnIndex = $clickedCell.index();
                    if (columnIndex !== 0) {
                        var data = table.row(this).data();
                        const url = "/devicevalues?device=" + encodeURIComponent(data.key);
                        window.location.href = url;
                    }
                }
            });

            });
        </script>
        """

        h.write(data)
        h.flush()

    def cb_alldevices(self, handler, params):
        """Present an html page with all known devices"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
            <div class="card p-4 p-lg-5">
            <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
            <div>
            <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
            <p class="text-secondary mb-0"><a href="/gateways">Gateways</a> / <b>devices</b></p>
            </div>
            <div class="text-muted small">{mbio.version} /
            <a href="/tasks">Tasks</a> /
            <a href="/values">Values</a> /
            <a href="/valuesmarked">Marks</a> /
            <a href="/zones">Zones</a>
            </div>
            </div>
            <table id="items" class="display nowrap" style="width:100%">
            <thead>
            <tr>
            <th data-priority="1">Gateway</th>
            <th data-priority="1">Address</th>
            <th data-priority="1">Key</th>
            <th data-priority="2">Vendor</th>
            <th data-priority="2">Model</th>
            <th data-priority="2">Version</th>
            <th data-priority="4">Upgrade</th>
            <th data-priority="1">State</th>
            <th data-priority="6">Age</th>
            <th data-priority="8">Error</th>
            <th data-priority="9">#Values</th>
            <th data-priority="10">#Msg</th>
            <th data-priority="10">#MsgErr</th>
            <th data-priority="2">Class</th>
            <th data-priority="1">Zone</th>
            <th data-priority="4">Reboot</th>
            </tr>
            </thead>
            </table>
            </div>
            </div>
        """
        h.write(data)

        data="""
        <script>
            $(function () {
            const table = new DataTable('#items', {
            responsive: true,
            paging: false,
            searching: true,
            ordering: true,
            info: false,
            search: {
                smart: true,
                regex: false,
                caseInsensitive: true,
                boundary: false
            },
            ajax: {
                url: "/api/v1/getalldevices",
                dataSrc: "data"
            },
            columns: [
                { data: "gateway" },
                { data: "address" },
                { data: "key" },
                { data: "vendor" },
                { data: "model" },
                { data: "version" },
                { data: "upgrade",
                    render: function (data, type, row) {
                        if (type !== "display") return data;
                        if (row.upgrade && !row.error) {
                        return `<div class="d-flex justify-content-between align-items-center">
                                <button class="btn btn-sm btn-outline-secondary cell-action"
                                    data-field="upgrade" data-id="${row.key}">
                                Upgrade
                                </button>
                                </div>`;
                        }
                        return '';
                    }
                },
                { data: "state",
                    render: function (data, type, row) {
                        if (type !== "display") return data;
                        return `<div class="d-flex justify-content-between align-items-center">
                            <span>${data}</span>
                            <button class="btn btn-sm btn-outline-secondary cell-action"
                                data-field="state" data-id="${row.key}">
                                Reset
                            </button>
                            </div>`;
                        }
                },
                { data: "statetime" },
                { data: "error", render: v=>v ? 'ERR' : 'OK' },
                { data: "countvalues" },
                { data: "countmsg" },
                { data: "countmsgerr" },
                { data: "class" },
                { data: "zone" },
                { data: "reboot",
                    render: function (data, type, row) {
                        if (type !== "display") return data;
                        if (row.reboot && !row.error) {
                        return `<div class="d-flex justify-content-between align-items-center">
                                <button class="btn btn-sm btn-outline-secondary cell-action"
                                    data-field="reboot" data-id="${row.key}">
                                Reboot
                                </button>
                                </div>`;
                        }
                        return '';
                    }
                }
            ],
            rowCallback: function (row, data) {
                if (data.error) {
                    $('td', row).css('background-color', 'pink');
                }
            }
            });

            setInterval(function () {
                table.ajax.reload(null, false);
                }, 2000);

            $("#items tbody").on("click", ".cell-action, .action-btn", async function (e) {
                e.stopPropagation();

                const $ui = $(this);
                const $tr    = $ui.closest('tr');
                const colKey = $ui.data('field');
                const rowApi = table.row($tr);
                const row    = rowApi.data();

                if (colKey=='state') {
                    try {
                        const r = await fetch(`/api/v1/resetdevice?key=${row.key}`, {method: "GET"});
                    } catch (err) {
                    }
                } else if (colKey=='reboot') {
                    try {
                        const r = await fetch(`/api/v1/rebootdevice?key=${row.key}`, {method: "GET"});
                    } catch (err) {
                    }
                } else if (colKey=='upgrade') {
                    try {
                        const r = await fetch(`/api/v1/upgradedevice?key=${row.key}`, {method: "GET"});
                    } catch (err) {
                    }
                }
            });

            $('#items').on('click','tr', function(e) {
                var $clickedCell = $(e.target).closest('td');
                if ($clickedCell.length) {
                    var columnIndex = $clickedCell.index();
                    if (columnIndex !== 0) {
                        var data = table.row(this).data();
                        const url = "/devicevalues?device=" + encodeURIComponent(data.key);
                        window.location.href = url;
                    }
                }
            });

            });
        </script>
        """
        h.write(data)

        h.flush()

    def cb_taskvalues(self, handler, params):
        """Present an html page with all MBIO values of a given task"""

        task=params.get('task')

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)
        h.variable('task', task)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><a href="/tasks">Tasks</a> / <b>{task}</b> / values</p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/gateways">Gateways</a> /
                    <a href="/values">Values</a> /
                    <a href="/valuesmarked">Marks</a> /
                    <a href="/zones">Zones</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Mark</th>
                            <th data-priority="1">Manual</th>
                            <th data-priority="1">Value</th>
                            <th data-priority="1">Setpoint</th>
                            <th data-priority="5">Flags</th>
                            <th data-priority="10">Age</th>
                            <th data-priority="9">#TX</th>
                            <th data-priority="6">Error</th>
                            <th data-priority="2">Tag</th>
                            <th data-priority="3">Label</th>
                            <th data-priority="2">Zone</th>
                        </tr>
                    </thead>
                    </table>
                    <div class="text-muted small">
                    [ / ] search, [CTRL+r] refresh values, [CTRL+k] mark values, [CTRL+K] unmark values
                    </div>
                </div>
            </div>
        """
        h.write(data)

        url=f"/api/v1/gettaskvalues?task={task}"
        data=self.getDataTableScriptForValues(url, 5000)
        h.write(data)

        h.flush()

    def cb_zonevalues(self, handler, params):
        """Present an html page with all MBIO values for a given zone"""

        zone=params.get('zone')

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)
        h.variable('zone', zone)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><a href="/zones">Zones</a> / <b>{zone}</b> / values</p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/gateways">Gateways</a> /
                    <a href="/devices">Devices</a> /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/values">Values</a> /
                    <a href="/valuesmarked">Marks</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Mark</th>
                            <th data-priority="1">Manual</th>
                            <th data-priority="1">Value</th>
                            <th data-priority="1">Setpoint</th>
                            <th data-priority="5">Flags</th>
                            <th data-priority="10">Age</th>
                            <th data-priority="9">#TX</th>
                            <th data-priority="6">Error</th>
                            <th data-priority="2">Tag</th>
                            <th data-priority="3">Label</th>
                            <th data-priority="2">Zone</th>
                        </tr>
                    </thead>
                    </table>
                    <div class="text-muted small">
                    [ / ] search, [CTRL+r] refresh values, [CTRL+k] mark values, [CTRL+K] unmark values
                    </div>
                </div>
            </div>
        """
        h.write(data)

        url=f"/api/v1/getzonevalues?zone={zone}"
        data=self.getDataTableScriptForValues(url, 5000)
        h.write(data)

        h.flush()

    def cb_devicevalues(self, handler, params):
        """Present an html page with all MBIO values of a given device"""

        mbio=self.getMBIO()

        device=params.get('device')
        d=mbio.device(device)
        gateway=None
        if d:
            gateway=d.gateway.key

        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)
        h.variable('gateway', gateway)
        h.variable('device', device)
        h.variable('url', f'/devices?gateway={gateway}')

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0"><a href="/gateways">Gateways</a> / <a href="{url}">{gateway}</a> / <b>{device}</b> / values</p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/tasks">Tasks</a> /
                    <a href="/values">Values</a> /
                    <a href="/valuesmarked">Marks</a> /
                    <a href="/zones">Zones</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Mark</th>
                            <th data-priority="1">Manual</th>
                            <th data-priority="1">Value</th>
                            <th data-priority="1">Setpoint</th>
                            <th data-priority="5">Flags</th>
                            <th data-priority="10">Age</th>
                            <th data-priority="9">#TX</th>
                            <th data-priority="6">Error</th>
                            <th data-priority="2">Tag</th>
                            <th data-priority="3">Label</th>
                            <th data-priority="2">Zone</th>
                        </tr>
                    </thead>
                    </table>
                    <div class="text-muted small">
                    [ / ] search, [CTRL+r] refresh values, [CTRL+k] mark values, [CTRL+K] unmark values
                    </div>
                </div>
            </div>
        """
        h.write(data)

        url=f"/api/v1/getdevicevalues?device={device}"
        data=self.getDataTableScriptForValues(url, 5000)
        h.write(data)

        h.flush()

    def getDataTableScriptForValues(self, url, timeoutReload=5000, enableMarkedView=False):
        data="""
        <script>
            $(function () {
					let isEditing = false;

                    const table = new DataTable('#items', {
                    rowId: 'key',
                    responsive: true,
                    paging: false,
                    searching: true,
                    ordering: true,
                    info: false,
                    search: {
                        smart: true,
                        regex: false,
                        caseInsensitive: true,
                        boundary: false
                    },
                    ajax: {
                        url: "{url}",
                        dataSrc: "data",
					},

                    columns: [
                    { data: "key" },
                    { data: "marked", className: "editable",
                            render: function(value, type, row) {
                                if (type === "display") {
                                    const checked = row.marked ? 'checked' : '';
                                    return `<label class="form-switch">
                                        <input type="checkbox" class="toggle-enabled"
                                        data-id="${row.key}" data-field="marked"
                                        ${checked}>
                                        <span class="slider"></span>
                                        </label>`;
                                 }

                                return value;
                            }
                        },
                    { data: "manual", className: "editable",
                            render: function(value, type, row) {
                                if (type === "display") {
                                    if (row.writable && !row.error)
                                    {
                                        const checked = row.manual ? 'checked' : '';
                                        return `<label class="form-switch">
                                            <input type="checkbox" class="toggle-enabled"
                                            data-id="${row.key}" data-field="manual"
                                            ${checked}>
                                            <span class="slider"></span>
                                            </label>`;
                                    }

                                    return row.manual ? "MAN" : "AUTO";
                                 }

                                return value;
                            }
                        },
                        { data: "valuestr", className: "text-end" },
                        { data: "toreachvalue", className: "p0 editable text-start",
                          render: function(value, type, row)
                          {
                                if (type === "display")
                                {
                                    if (row.manual && row.writable)
                                    {
                                        if (row.digital)
                                        {
                                            const checked = row.toreachvalue ? 'checked' : '';
                                            return `<label class="form-switch">
                                                <input type="checkbox" class="toggle-enabled"
                                                data-id="${row.key}" data-field="toreachvalue"
                                                ${checked}>
                                                <span class="slider"></span>
                                                </label>`;
                                        }
                                        else
                                        {
                                            return `<input type="number" class="form-control form-control-sm edit-input"
                                                    data-id="${row.key}" data-field="toreachvalue"
                                                    value="${value ?? ''}">`;
                                        }
                                    }
                                 }

                                return value;
                            }
                        },
                        { data: "flags" },
                        { data: "notifycount" },
                        { data: "age", render: v=>v<3600 ? v : '' },
                        { data: "error", render: v=>v ? 'ERR' : 'OK' },
                        { data: "tag" },
                        { data: "description" },
                        { data: "zone" }
                    ],

                    rowCallback: function (row, data) {
                        if (!data.enable) {
                            $('td', row).css('background-color', 'lightgray');
                        } else if (data.error) {
                            $('td', row).css('background-color', 'pink');
                        } else if (data.manual) {
                            $('td', row).css('background-color', 'lightgreen');
                        } else if (data.marked) {
                            $('td', row).css('background-color', 'lightyellow');
                        } else {
                            $('td', row).css('background-color', 'white');
                        }
                    }
                });

                async function reloadRow(table, row) {
                    try {
                        data=row.data();
                        var r = await fetch(`/api/v1/getvalues?key=${data.key}`, {method: "GET"}).then(r=>r.json());
                        var newdata=r.data[0];
                        row.data(newdata);
                        row.invalidate();

                        table.draw(false);
						return true;

                    } catch (_) {
                    }
                }

                async function markRow(row) {
                    try {
                        data=row.data();
                        var r = await fetch(`/api/v1/markvalue?key=${data.key}`, {method: "GET"}).then(r=>r.json());
                    } catch (_) {
                    }
                }

                async function markZone(zone) {
                    try {
						if (zone) {
							var r = await fetch(`/api/v1/markvaluewithzone?zone=${zone}`, {method: "GET"}).then(r=>r.json());
						}
                    } catch (_) {
                    }
                }

                async function unmarkRow(row) {
                    try {
                        data=row.data();
                        var r = await fetch(`/api/v1/unmarkvalue?key=${data.key}`, {method: "GET"}).then(r=>r.json());
                    } catch (_) {
                    }
                }

                const enableMarkedView={enablemarkedview};

                let pollingId = setInterval(function() {
					if (isEditing) return;
					table.ajax.reload(null, false);
                  }, {timeout});

               // Quand l'utilisateur commence à éditer un input dans le tableau
               $('#items tbody').on('focus', 'input', function () {
					isEditing=true;
                });

                // Quand il termine (blur), on “dégèle” la ligne
                $('#items tbody').on('blur', 'input', function () {
					isEditing=false;
                });

                $("#items tbody").on("change", ".toggle-enabled", async function (e) {
                    //clearInterval(pollingId);
                    e.stopPropagation();

                    const $ui = $(this);
                    if ($ui.data('committing')) return;       // garde-fou
                    $ui.data('committing', true);

                    const $tr    = $ui.closest('tr');
                    const colKey = $ui.data('field');
                    const enabled = $ui.is(':checked');
                    const rowApi = table.row($tr);
                    const row    = rowApi.data();

                    try {
                        var res;
                        var digital=row.digital;

                        if (colKey=="toreachvalue") {
                            if (enabled) {
                                res = await fetch(`/api/v1/setvalue?key=${row.key}&value=1`, {method: "GET"});
                            } else {
                                res = await fetch(`/api/v1/setvalue?key=${row.key}&value=0`, {method: "GET"});
                            }

                            if (enableMarkedView) {
                                rows=table.rows({ search: 'applied' });
                                var count=0;
                                rows.every(function () {
                                    if (count<MAXVALUESATONCE)
                                    {
                                        data=this.data();
                                        if (data.digital==digital && data.writable && !data.error)
                                        {
                                            if (enabled)
                                            {
                                                fetch(`/api/v1/setvalue?key=${data.key}&value=1`, {method: "GET"});
                                                reloadRow(table, this);
                                                count++;
                                            }
                                            else
                                            {
                                                fetch(`/api/v1/setvalue?key=${data.key}&value=0`, {method: "GET"});
                                                reloadRow(table, this);
                                                count++;
                                            }
                                        }
                                    }
                                });
                            }
                        }
                        else if (colKey=="marked") {
                            if (enabled) {
                                res = await fetch(`/api/v1/markvalue?key=${row.key}`, {method: "GET"});
                            } else {
                                res = await fetch(`/api/v1/unmarkvalue?key=${row.key}`, {method: "GET"});
                            }
                        }
                        else {
                            if (enabled) {
                                v=row.toreachvalue;
                                if (v === null)
                                    v=row.value;
                                res = await fetch(`/api/v1/setvalue?key=${row.key}&value=${v}`, {method: "GET"});
                            } else {
                                res = await fetch(`/api/v1/setvalueauto?key=${row.key}`, {method: "GET"});
                            }

                            if (enableMarkedView) {
                                rows=table.rows({ search: 'applied' });
                                var count=0;
                                rows.every(function () {
                                    if (count<MAXVALUESATONCE)
                                    {
                                        data=this.data();
                                        if (data.digital==digital && data.writable && !data.error)
                                        {
                                            if (enabled)
                                            {
                                                v=data.toreachvalue;
                                                if (v === null)
                                                    v=data.value;
                                                fetch(`/api/v1/setvalue?key=${data.key}&value=${v}`, {method: "GET"});
                                                reloadRow(table, this);
                                                count++;
                                            }
                                            else
                                            {
                                                fetch(`/api/v1/setvalueauto?key=${data.key}`, {method: "GET"});
                                                reloadRow(table, this);
                                                count++;
                                            }
                                        }
                                    }
                                });
                            }
                        }

                        reloadRow(table, rowApi);

						/*
                        pollingId = setInterval(function() {
                            table.ajax.reload(null, false);
                            }, {timeout});
						*/

                        if (!res.ok) throw new Error();
                    } catch (_) {
                        //$(this).prop("checked", !enabled);
                        console.log("value set error!");
                    } finally {
                        $ui.data('committing', false);
                    }
                });

                // ENTER => on empêche la soumission et on force le blur (ce qui déclenchera 'change')
                $('#items tbody').on('keydown', 'input.edit-input', function (e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.blur(); // provoque un 'change' si la valeur a été modifiée
                    }
                });

                // CHANGE (et donc aussi BLUR si la valeur a changé) => commit
                $('#items tbody').on('change', 'input.edit-input', async function () {
					const $ui = $(this);
					if ($ui.data('committing')) return;       // garde-fou
					$ui.data('committing', true);

					const colKey = $ui.data('field');
					const $tr    = $ui.closest('tr');
					const rowApi = table.row($tr);
					const row    = rowApi.data();

                    const original = row[colKey];
                    let newVal = $ui.val().trim();

                    if (String(original) === String(newVal)) {
                        $ui.data('committing', false);
                        return;
                    }

                    try {
                        const res = await fetch(`/api/v1/setvalue?key=${row.key}&value=${newVal}`, {method: 'GET'});
                        row[colKey] = newVal;
                        rowApi.data(row).draw(false);

                        if (enableMarkedView) {
                            rows=table.rows({ search: 'applied' });
                            var count=0;
                            rows.every(function () {
                                if (count<MAXVALUESATONCE)
                                {
                                    data=this.data();
                                    if (data.writable && data.manual && !data.error && !data.digital)
                                    {
                                        fetch(`/api/v1/setvalue?key=${data.key}&value=${newVal}`, {method: "GET"});
                                        reloadRow(table, this);
                                        count++;
                                    }
                                }
                            });
                        }
                    } catch (err) {
                    } finally {
                        $ui.data('committing', false);
                    }
                });

                const MAXVALUESATONCE=128;
                /*
				var activezone='';
                $('#items tbody').on('mouseenter', 'tr', function () {
					var row = table.row(this);
					var data = row.data();
					activezone=data.zone;
				});
                */

                $(document).on('keydown', function (e) {
                    const $target=$(e.target);
                    const $searchInput = $('#dt-search-0.dt-input');

                    if (!e.ctrlKey && !e.metaKey && !e.altKey && e.key === '/') {
                        e.preventDefault();
                        $searchInput.focus();
                        $searchInput.select();
                    } else if (e.ctrlKey && !e.metaKey && !e.altKey && e.key.toLowerCase() === 'r') {
                        e.preventDefault();
                        rows=table.rows({ search: 'applied' });
                        if (rows.count()>0)
                        {
                            var count=0;
                            rows.every(function () {
                                if (count<MAXVALUESATONCE)
                                {
                                    reloadRow(table, this);
                                    count++;
                                }
                            });
                        }
                    } else if (e.ctrlKey && !e.metaKey && !e.altKey && e.key === 'k') {
                        e.preventDefault();
                        rows=table.rows({ search: 'applied' });
                        var count=0;
                        rows.every(function () {
                            if (count<MAXVALUESATONCE)
                            {
                                data=this.data();
                                if (!data.marked)
                                {
                                    markRow(this);
                                    reloadRow(table, this);
                                    count++;
                                }
                            }
                        });
                    } else if (e.ctrlKey && !e.metaKey && !e.altKey && e.key === 'K') {
                        e.preventDefault();
                        rows=table.rows({ search: 'applied' });
                        var count=0;
                        rows.every(function () {
                            if (count<MAXVALUESATONCE)
                            {
                                data=this.data();
                                if (data.marked)
                                {
                                    unmarkRow(this);
                                    reloadRow(table, this);
                                    count++;
                                }
                            }
                        });
                    } else if (e.ctrlKey && !e.metaKey && !e.altKey && e.key === 'z') {
                        /*
                        e.preventDefault();
						markZone(activezone);
                        rows=table.rows({ search: 'applied' });
                        if (rows.count()>0)
                        {
                            var count=0;
                            rows.every(function () {
                                if (count<MAXVALUESATONCE)
                                {
                                    reloadRow(table, this);
                                    count++;
                                }
                            });
                        }
                        */
                    }
                });

            });
        </script>
        """

        data=data.replace('{url}', url)
        enable='false'
        if enableMarkedView:
            enable='true';
        data=data.replace('{enablemarkedview}', enable)
        data=data.replace('{timeout}', str(timeoutReload))

        return data

    def cb_values(self, handler, params):
        """Present an html page with all MBIO values"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0">MBIO /
                        <b>Values</b> [<a href="/valuesmanual">MANUALS</a>]
                        [<a href="/valueserror">ERRORS</a>]
                        [<a href="/valuesmarked">MARKED</a>]</p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/gateways">Gateways</a> /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/tasks">Tasks</a> /
                    <a href="/valuesmarked">Marks</a> /
                    <a href="/zones">Zones</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Mark</th>
                            <th data-priority="1">Manual</th>
                            <th data-priority="1">Value</th>
                            <th data-priority="1">Setpoint</th>
                            <th data-priority="5">Flags</th>
                            <th data-priority="10">Age</th>
                            <th data-priority="9">#TX</th>
                            <th data-priority="6">Error</th>
                            <th data-priority="2">Tag</th>
                            <th data-priority="3">Label</th>
                            <th data-priority="2">Zone</th>
                        </tr>
                    </thead>
                    </table>
                    <div class="text-muted small">
                    [ / ] search, [CTRL+r] refresh values, [CTRL+k] mark values, [CTRL+K] unmark values
                    </div>
                </div>
            </div>
        """
        h.write(data)

        data=self.getDataTableScriptForValues('/api/v1/getvalues', 10000)
        h.write(data)

        h.flush()

    def cb_valuesmanual(self, handler, params):
        """Present an html page with MBIO values that are currently in manual"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                        <div>
                            <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                            <p class="text-secondary mb-0">MBIO / <a href="/values">Values</a> (<b>MANUALS ONLY</b>)</p>
                        </div>
                        <div class="text-muted small">{mbio.version} /
                            <a href="/gateways">Gateways</a> /
                            <a href="/alldevices">*Devices</a> /
                            <a href="/tasks">Tasks</a> /
                            <a href="/valuesmarked">Marks</a> /
                            <a href="/zones">Zones</a>
                        </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                        <thead>
                            <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Mark</th>
                            <th data-priority="1">Manual</th>
                            <th data-priority="1">Value</th>
                            <th data-priority="1">Setpoint</th>
                            <th data-priority="5">Flags</th>
                            <th data-priority="10">Age</th>
                            <th data-priority="9">#TX</th>
                            <th data-priority="6">Error</th>
                            <th data-priority="2">Tag</th>
                            <th data-priority="3">Label</th>
                            <th data-priority="2">Zone</th>
                            </tr>
                        </thead>
                    </table>
                    <div class="text-muted small">
                    [ / ] search, [CTRL+r] refresh values, [CTRL+k] mark values, [CTRL+K] unmark values
                    </div>
                </div>
            </div>
        """
        h.write(data)

        data=self.getDataTableScriptForValues('/api/v1/getvalues?manual=1', 5000)
        h.write(data)

        h.flush()

    def cb_valueserror(self, handler, params):
        """Present an html page with MBIO values that are currently in error"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0">MBIO / <a href="/values">Values</a> (<b>ERRORS ONLY</b>)</p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/gateways">Gateways</a> /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/tasks">Tasks</a> /
                    <a href="/valuesmarked">Marks</a> /
                    <a href="/zones">Zones</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Mark</th>
                            <th data-priority="1">Manual</th>
                            <th data-priority="1">Value</th>
                            <th data-priority="1">Setpoint</th>
                            <th data-priority="5">Flags</th>
                            <th data-priority="10">Age</th>
                            <th data-priority="9">#TX</th>
                            <th data-priority="6">Error</th>
                            <th data-priority="2">Tag</th>
                            <th data-priority="3">Label</th>
                            <th data-priority="2">Zone</th>
                        </tr>
                    </thead>
                    </table>
                    <div class="text-muted small">
                    [ / ] search, [CTRL+r] refresh values, [CTRL+k] mark values, [CTRL+K] unmark values
                    </div>
                </div>
            </div>
        """
        h.write(data)

        data=self.getDataTableScriptForValues('/api/v1/getvalues?error=1', 5000)
        h.write(data)

        h.flush()

    def cb_valuesmarked(self, handler, params):
        """Present an html page with MBIO values that are currently marked"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                    <div>
                        <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                        <p class="text-secondary mb-0">MBIO / <a href="/values">Values</a> (<b>MARKED ONLY</b>)</p>
                    </div>
                    <div class="text-muted small">{mbio.version} /
                    <a href="/gateways">Gateways</a> /
                    <a href="/alldevices">*Devices</a> /
                    <a href="/tasks">Tasks</a> /
                    <a href="/zones">Zones</a>
                    </div>
                    </div>
                    <table id="items" class="display nowrap" style="width:100%">
                    <thead>
                        <tr>
                            <th data-priority="1">Key</th>
                            <th data-priority="1">Mark</th>
                            <th data-priority="1">Manual</th>
                            <th data-priority="1">Value</th>
                            <th data-priority="1">Setpoint</th>
                            <th data-priority="5">Flags</th>
                            <th data-priority="10">Age</th>
                            <th data-priority="9">#TX</th>
                            <th data-priority="6">Error</th>
                            <th data-priority="2">Tag</th>
                            <th data-priority="3">Label</th>
                            <th data-priority="2">Zone</th>
                        </tr>
                    </thead>
                    </table>
                    <div class="text-muted small">
                    [ / ] search, [CTRL+r] refresh values, [CTRL+k] mark values, [CTRL+K] unmark values
                    </div>
                </div>
            </div>
        """
        h.write(data)

        data=self.getDataTableScriptForValues('/api/v1/getvalues?marked=1', 5000, True)
        h.write(data)

        h.flush()

    def cb_zoneeditor(self, handler, params):
        """Zone editor"""

        h=Html(None, handler)
        h.readFile('ws-zoneeditor.html')
        h.flush()

    def cb_script_zoneeditor(self, handler, params):
        """Zone editor script"""

        h=Html(None, handler)
        h.variable('interface', self._hostcpu or 'localhost')
        h.variable('port', self.wserver._port or 8001)

        h.readFile('ws-script-zoneeditor.js')
        h.flush()

    def cb_help(self, handler, params):
        """API reference"""

        mbio=self.getMBIO()
        h=HtmlPage('Digimat MBIO Processor Monitor', handler)
        h.variable('mbio.version', mbio.version)

        data="""
            <div class="page container-fluid">
                <div class="card p-4 p-lg-5">
                    <div class="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-3">
                        <div>
                            <h1 class="h3 mb-1">Digimat MBIO Processor Monitor</h1>
                            <p class="text-secondary mb-0">API reference</p>
                        </div>
                        <div class="text-muted small">{mbio.version} /
                            <a href="/gateways">Gateways</a> /
                            <a href="/alldevices">*Devices</a> /
                            <a href="/tasks">Tasks</a>
                        </div>
                    </div>
        """
        h.write(data)

        for cb in self._wserver._callbacks['GET']:
            if cb=='/':
                continue

            h.variable('href', cb)
            f=self._wserver._callbacks['GET'][cb]
            doc=f.__doc__

            h.write('<p><a href="{href}">')
            h.write(cb)
            h.write('</a>')
            if doc:
                h.write('<br>')
                h.write(doc)

        data="""</div>
            </div>
        """
        h.write(data)

        h.flush()

    def onLoad(self, xml: XMLConfig):
        mbio=self.getMBIO()
        port=xml.getInt('port', 8001)
        # deny reserved ports
        if port in [8000]:
            port=8001
        # interface=mbio.interface
        interface='0.0.0.0'
        self._hostcpu=mbio.resolveIpAliasToIpAddress('cpu')
        if self._hostcpu=='cpu':
            self._hostcpu='localhost'

        ws=TemporaryWebServer('/tmp/wsmonitor', port=port, host=interface, logger=self.logger)
        if ws:
            self._wserver=ws
            ws.registerGetCallback('/api/v1/gettasks', self.cb_gettasks)
            ws.registerGetCallback('/api/v1/getzones', self.cb_getzones)
            ws.registerGetPostCallback('/api/v1/setzone', self.cb_setzone)
            ws.registerGetCallback('/api/v1/getgateways', self.cb_getgateways)
            ws.registerGetCallback('/api/v1/getgatewaydevices', self.cb_getgatewaydevices)
            ws.registerGetCallback('/api/v1/getalldevices', self.cb_getalldevices)
            ws.registerGetCallback('/api/v1/gettaskvalues', self.cb_gettaskvalues)
            ws.registerGetCallback('/api/v1/getzonevalues', self.cb_getzonevalues)
            ws.registerGetCallback('/api/v1/getdevicevalues', self.cb_getdevicevalues)
            ws.registerGetCallback('/api/v1/getvalues', self.cb_getvalues)
            ws.registerGetCallback('/api/v1/setvalue', self.cb_setvalue)
            ws.registerGetCallback('/api/v1/setvalueauto', self.cb_setvalueauto)
            ws.registerGetCallback('/api/v1/markvalue', self.cb_markvalue)
            ws.registerGetCallback('/api/v1/markvaluewithzone', self.cb_markvaluewithzone)
            ws.registerGetCallback('/api/v1/unmarkvalue', self.cb_unmarkvalue)
            ws.registerGetCallback('/api/v1/resettask', self.cb_resettask)
            ws.registerGetCallback('/api/v1/resetgateway', self.cb_resetgateway)
            ws.registerGetCallback('/api/v1/resetdevice', self.cb_resetdevice)
            ws.registerGetCallback('/api/v1/rebootdevice', self.cb_rebootdevice)
            ws.registerGetCallback('/api/v1/upgradedevice', self.cb_upgradedevice)
            ws.registerGetCallback('/api/v1/save', self.cb_save)
            ws.registerGetCallback('/api/v1/beep', self.cb_beep)
            ws.registerGetCallback('/api/v1/getuserdata', self.cb_getuserdata)
            ws.registerGetPostCallback('/api/v1/storeuserdata', self.cb_storeuserdata)

            ws.registerGetCallback('/script/zoneeditor.js', self.cb_script_zoneeditor)

            ws.registerGetCallback('/tasks', self.cb_tasks)
            ws.registerGetCallback('/zones', self.cb_zones)
            ws.registerGetCallback('/gateways', self.cb_gateways)
            ws.registerGetCallback('/devices', self.cb_devices)
            ws.registerGetCallback('/alldevices', self.cb_alldevices)
            ws.registerGetCallback('/taskvalues', self.cb_taskvalues)
            ws.registerGetCallback('/zonevalues', self.cb_zonevalues)
            ws.registerGetCallback('/devicevalues', self.cb_devicevalues)
            ws.registerGetCallback('/values', self.cb_values)
            ws.registerGetCallback('/valuesmanual', self.cb_valuesmanual)
            ws.registerGetCallback('/valueserror', self.cb_valueserror)
            ws.registerGetCallback('/valuesmarked', self.cb_valuesmarked)
            ws.registerGetCallback('/monitor', self.cb_gateways)
            ws.registerGetCallback('/', self.cb_alldevices)
            ws.registerGetCallback('/zoneeditor', self.cb_zoneeditor)

            ws.registerGetCallback('/help', self.cb_help)

    def poweron(self):
        ws=self.wserver
        if ws:
            ws.disableAutoShutdown()
            ws.linkPath('~/Dropbox/python/www')
            ws.linkPath('/usr/lib/www')
            ws.start()
        return True

    def poweroff(self):
        ws=self.wserver
        if ws:
            ws.stop()
        return True

    def run(self):
        return 0.1


if __name__ == "__main__":
    pass
