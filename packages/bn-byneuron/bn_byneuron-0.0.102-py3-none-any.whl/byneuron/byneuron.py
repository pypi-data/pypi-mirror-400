import datetime
import uuid
import requests
import json
from configparser import ConfigParser
import os
import sys
import glob
import logging
from itertools import chain

log = logging.getLogger('byneuron')


class ByConfig:
    DEFAULT_INI_FILENAME = '*.ini'
    DEFAULT_INI_SECTION = 'byneuron'

    def __init__(self, api=None, login=None, key=None, secret=None):
        logging.basicConfig(level=logging.INFO)
        log.info('init Byneuron Config')
        self.url_api = None if api is None else api
        self.url_login = None if login is None else login
        self.client_id = key if key else None
        self.client_secret = secret if secret else None
        # login using username > not supported
        # self.user_id = key if key else None
        # self.user_key = secret if secret else None
        self.get_env()
        self.get_ini(self.DEFAULT_INI_FILENAME, 'byneuron')
        if not self.valid():
            log.debug('config: %s', vars(self))
            raise ValueError('invalid configuration')

    def valid(self):
        return self.valid_client()

    def valid_client(self):
        if None not in {self.client_id, self.client_secret}:
            return True

    # def valid_user(self):
    #     if None not in {self.user_id, self.user_key}:
    #         return True

    def get_env(self):
        def setter(attr, option):
            if self.__getattribute__(attr) is None and option in os.environ:
                log.info('config set %s from environment', option)
                self.__setattr__(attr, os.environ[option])

        setter('url_api', 'BYNEURON_URL')
        setter('url_login', 'KEYCLOAK_TOKEN_URL')
        setter('client_id', 'OAUTH2_CLIENT_ID')
        setter('client_secret', 'OAUTH2_CLIENT_SECRET')
        # setter('user_id', 'OAUTH2_CLIENT_ID')
        # setter('user_key', 'OAUTH2_CLIENT_SECRET')

        if not self.valid():
            log.debug('no config in environment, continue')

    def get_ini(self, filename=None, section=None):
        def setter(attr, conf, option):
            if self.__getattribute__(attr) is None and option in conf[section]:
                log.info('config set %s from %s', option, filename)
                self.__setattr__(attr, conf[section][option])

        if self.valid():
            return
        if filename is None:
            filename = self.DEFAULT_INI_FILENAME
        if section is None:
            section = self.DEFAULT_INI_SECTION
        files = self.path_search(filename)
        if files:
            log.info('configparser from ini files: %s', files)
            cp = ConfigParser()
            cp.read(files)
            if section in cp:
                setter('url_api', cp, 'url.api')
                setter('url_login', cp, 'url.login')
                setter('client_id', cp, 'client.id')
                setter('client_secret', cp, 'client.secret')
                # setter('user_id', cp, 'user.id')
                # setter('user_key', cp, 'user.secret')
            else:
                log.info('section %s not found in %s', section, filename)
        else:
            log.info('ini not available')

    def path_search(self, filename=None):
        if filename is None:
            filename = self.DEFAULT_INI_FILENAME
        root = os.path.dirname(os.path.abspath(sys.argv[0]))
        patterns = [
            f'{root}/**/{filename}',  # case: run directly from local project
            f'**/{filename}'  # case: imported as package in remote project
        ]
        files = []
        for p in patterns:
            files.extend(glob.glob(p, recursive=True))
        return files


class Byneuron:
    def __init__(self, api=None, login=None, key=None, secret=None):
        self.config = ByConfig(api, login, key, secret)
        self.api = f'{self.config.url_api}/api/v1'
        self._token = ''
        self._token_expire = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        self._publicIdTypes = None
        self._isc = None
        # load indexSets for user and set one as default
        self.indexsets = []
        self.indexsets = self.get_indexsets()
        self.indexset_active = self.indexsets[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            log.error("Error Type: {}, \nError: {}\n".format(exc_type.__name__, exc_val))

    @property
    def now(self):
        """timezone aware utc now"""
        return datetime.datetime.now(datetime.timezone.utc)

    def recent(self, pattern: str = 'h', offset: int = None):
        """
        Round the current time to the start of last minute/hour/day/month

        for compatibility;
        pattern's digits are interpreted as offset of d, M, Y;
        examples:
        > recent('1d') == recent('d',0) == today at 00:00:00.0
        > recent('d',1) == yesterday at 00:00:00.0
        > recent('1d',1) == Last week on Monday at 00:00:00.0

        :param pattern: 'm', 'h', 'd', 'M', 'Y'
        :param offset: steps to shift the result back in time; negative values forward time
        :return: datetime object
        """
        n = self.now.replace(second=0, microsecond=0)
        if not isinstance(pattern, str):
            return n
        d, p = (int(pattern[:-1]), pattern[-1]) if len(pattern) > 1 else (1, pattern)
        if p == 'm':
            n = n.replace(minute=d * (n.minute // d))
            if offset:
                n -= datetime.timedelta(minutes=offset)
        elif p == 'h':
            n = n.replace(hour=d * (n.hour // d), minute=0)
            if offset:
                n -= datetime.timedelta(hours=offset)
        elif p == 'd':  # day of the week
            n = n.replace(hour=0, minute=0)
            # process as isoweekday if d and offset are both not None
            if offset is not None and bool(pattern in ['1d', '2d', '3d', '4d', '5d', '6d', '7d']):
                while n.isoweekday() != d:
                    n -= datetime.timedelta(days=1)
                if offset:
                    n -= datetime.timedelta(days=offset * 7)
            else:
                n -= datetime.timedelta(days=d - 1 if offset is None else offset)
        elif p == 'M':  # 1M > this month; 2M move one more month
            n = n.replace(day=1, hour=0, minute=0)
            offset = d - 1 if offset is None else offset
            n = n.replace(year=n.year + (n.month - offset - 1) // 12,
                          month=(n.month - offset - 1) % 12 + 1)
        elif p == 'Y':  # 1Y > round to start of year, 2Y > moves one more year
            offset = d - 1 if offset is None else offset
            n = n.replace(year=n.year - offset, month=1, day=1, hour=0, minute=0)
        return n

    @property
    def headers(self):
        """default header for API"""
        return {'Authorization': 'Bearer {}'.format(self.token)}

    @property
    def token(self):
        """triggers login if needed"""
        if self._token == '' or self.now >= self._token_expire:
            self.set_token()
        return self._token

    def set_token(self):
        data = self._login() or {}
        log.debug('set _token from data \n%s ', json.dumps(data, indent=2))
        self._token = data.get('access_token', '')
        self._token_expire = self.now \
                             + datetime.timedelta(seconds=data.get('expires_in', 0)) \
                             - datetime.timedelta(seconds=10)  # buffer for issue with token fail short before expire

    def del_token(self):
        """removes token, will force new login on next url"""
        self._token = ''
        self._token_expire = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

    def url(self, url, headers=None, data=None, as_json=True, params=None, action=None):
        log.debug('requests url %s', url)
        if action is None:
            action = 'POST' if isinstance(data, dict) else 'GET'
        if headers is None:
            headers = self.headers
        if action == 'POST':
            if as_json:
                log.debug('request.post json \n%s \n%s \n%s', url, headers, data)
                r = requests.post(url, headers=headers, json=data, params=params)
            else:
                r = requests.post(url, headers=headers, data=data, params=params)
                log.debug('request.post data \n%s \n%s \n%s', url, headers, data)
        elif action == 'GET':
            r = requests.get(url, headers=headers, params=params)
            log.debug('request.get \n%s \n%s', url, headers)
        else:
            return
        if r.status_code == 200:
            return r.json()  # returns a dict
        else:
            r.raise_for_status()

    def get_indexset(self, x=None):
        """
        retrieves indexset entity
        - active indexset
        - name, key
        - validates entity
        :param x: input to check
        :return: indexset or None
        """
        if x is None:
            return self.indexset_active
        if isinstance(x, str):
            for i in self.indexsets:
                if i.key == x or i.name == x:
                    return i
        if isinstance(x, Entity) and x.entity_type == 'IndexSet':
            return x

    def set_indexset(self, e, verbose=True):
        """
        analogy of selecting a tenant in frontend
        :param e: Entity of type IndexSet; indexset_key; indexset_name
        :param verbose: disable welcome message
        :return:
        """
        e = self.get_indexset(e)
        if e is not None:
            if verbose:
                log.info('Welcome to tenant %s', e.name)
            self.indexset_active = e

    def iter_indexset(self):
        for e in self.indexsets:
            self.set_indexset(e, True)
            yield self.indexset_active

    def publicids(self, entitytype):
        if self._publicIdTypes is None:
            self._publicIdTypes = [e.entity_type_ref for e in self.get_entities('PublicId') if isinstance(e, Entity)]
            log.debug('publicids', self._publicIdTypes)
        return entitytype in self._publicIdTypes

    ### endpoints ##
    def _login(self):
        login_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        if not self.config.valid_client():
            raise ValueError('missing client credentials')
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "client_credentials"
        }
        url = self.config.url_login
        """
        if url is None:
            # note this endpoint is no longer used.
            url = f'{self.api}/login'
        """
        r = self.url(url=url, headers=login_headers, data=data, as_json=False)
        return r

    def _datamodel(self):
        url = f'{self.api}/backend/rest/datamodel'
        return self.url(url=url)

    def _graphql(self, query, references=None):
        """
        graphql query array eg ["CodeType:?codeTypes entity:type CodeType."]
        default retrieve ?indexSet
        :returns {'codeTypes':{'id':{object}}}
        """
        query = "\n".join(query) if isinstance(query, list) else f'{query}'
        references = references if isinstance(references, dict) else {}
        data = {
            "query": query,
            "references": references
        }
        url = f'{self.api}/backend/rest/datamodel/_graphql'
        log.debug('_graphql %s', data)
        return self.url(url=url, data=data)

    def _graphmodel(self, data):
        """ create / edit entities and events into the model"""
        entities = {}
        numberevents = []
        if not isinstance(data, list):
            data = [data]
        for d in data:
            if isinstance(d, Entity):
                entities.update({d.key: d.wrap()})
            elif isinstance(d, Numberevent):
                numberevents.append(d.wrap())
        data = {
            "entityDataModel": {"nodes": entities},
            "numberEventDataModel": {"events": numberevents}
        }
        log.debug('graphmodel, data: \n%s', json.dumps(data, indent=2))
        url = f'{self.api}/backend/tasks/entities/graphmodel'
        return self.url(url=url, data=data)

    def _publicid(self, entitytype, indexset=None):
        if self.publicids(entitytype):
            data = {
                "indexSet": indexset.key if indexset else self.indexset_active.key,
                "entityType": f'com.bynubian.shared.entities.{entitytype}',
                "fieldName": 'publicId',
                "date": self.now.strftime('%Y-%m-%d')
            }
            url = f'{self.api}/backend/rest/publicids/generate'
            r = self.url(url=url, data=data)
            if r:
                return r.get('publicId')

    def _openapi(self, endpoint, action='GET', tenant=None, params=None, data=None):
        endpoints = {
            'timeseries': 'Item',
            'asset': 'Device',
            'site': 'Place'
        }

        tenant = self.get_indexset(tenant).name
        url = f'{self.api}/{tenant}/{endpoint}'
        r = self.url(url=url, data=data, params=params, action=action)

        if isinstance(r, list):
            for i in r:
                # temporary fix
                yield self.get_entity(endpoints.get(endpoint), key=i.get('identification').get('id'))

                # yield Entity(openapi=i)

    def _data_indexsets(self, indexsets):
        """
        used for event and entity queries
        :param indexsets: (list of) entities or indexsetKeys, indexsetNames,
        special cases: None, use active indexset; True: use all indexsets
        :return:
        """
        indexset_list = indexsets if isinstance(indexsets, list) else [indexsets]
        indexset_keys = set()
        for i in indexset_list:
            if i is True:
                indexset_keys.update({i.indexset for i in self.indexsets})  # all indexsets
            elif isinstance(i, Entity):
                indexset_keys.update({i.indexset})
            elif isinstance(i, str):
                e = self.get_indexset(i)
                if e:
                    indexset_keys.update({e.key})
                elif e is None:
                    # case: an entity.key is used
                    indexset_keys.update({self.indexset_active.key})
            elif i is None:
                indexset_keys.update({self.indexset_active.key})
        return list(indexset_keys)

    def _data_sort(self, order):
        return 'DESC' if order == 'DESC' else 'ASC'

    def _data_timestamp(self, dt):
        if isinstance(dt, datetime.datetime):
            return int(1000 * dt.timestamp())

    def _numberevents(self, size=100, order=None, deleted=False, indexsets=None, filters=None):
        """
        :param size:
        :param order:
        :param deleted:
        :param indexsets: list of indexSetKeys, Entities, else active indexSet is set
        :param filters:
        :return:
        """
        filters = [] if not isinstance(filters, list) else filters
        data = {
            "indexSets": self._data_indexsets(indexsets),  # list of indexSet keys
            "order": self._data_sort(order),
            # "ASC","DESC"  # order is respected after 'size' number of most recent events
            # have been collected; so "DESC" gives the most consistent result
            "size": int(size),
            "deleted": bool(deleted),
            "filters": filters,
            "esDocumentType": "NumberEvent"
        }
        url = f'{self.api}/backend/rest/numberevents/_query'
        log.debug('data for _numberevents %s', data)
        return self.url(url=url, data=data)

    def _datehistogramtimeline(self, items, aggrs, from_date, to_date, interval,
                               filters=None, gap=None, order=None, deleted=None):
        """
        :param items: (list of) entity of the type Item, or entity.key if in active indexset
        :param aggrs: list of aggregations, e.g. ['avg']
        :param from_date: date to start aggregation from
        :param to_date: end date to end aggregation with
        :param interval: 'bucket size' e.g. 15m
        :param filters: optional, method to e.g. include numberValue filtering
        :param gap: optional, specify gapstrategy
        :param order: optional, sorting on timestamp
        :param deleted: optional, include deleted events
        :return:
        """

        items = items if isinstance(items, list) else [items]
        timeseries = [i.key if isinstance(i, Entity) else i for i in items]
        agg_metrics = ['avg', 'min', 'max', 'count', 'diff', 'sum', 'close', 'cardinality', 'open']
        aggrs = [{
            "type": "metric",
            "name": m,
            "stat": m,
            "field": "numberValue"
        } for m in aggrs if m in agg_metrics]
        filters = filters if isinstance(filters, list) else []
        filters.append({
            "type": "eventitemid",
            "values": timeseries,
            "invertFilter": False,
            "operator": "or"
        })
        filters.append({
            "type": "range",  # this is sended as be UTC
            "from": self._data_timestamp(from_date),
            "to": self._data_timestamp(to_date),
            "minInclusive": True,
            "maxInclusive": False,
            "invertFilter": False
        })
        aggregation = {
            "type": "date",
            "field": "timestamp",  # todo alternatives? byneuronUpdated, byneuronCreated
            "time_zone": "UTC",  # "Africa/Nairobi" >> important on how we wrap results
            "interval": interval,
            "name": "datehistogram",
            "from": self._data_timestamp(from_date),
            # wierldly, this 'from' is a requirement to retrieve data with gapstrategy on
            "to": self._data_timestamp(to_date),
            "aggregations": aggrs
        }
        data = {
            "query": {
                "indexSets": self._data_indexsets(items),
                "sortField": "timestamp",
                "order": self._data_sort(order),
                "deleted": False if deleted is None else bool(False),
                "filters": filters,
                "esDocumentType": "NumberEvent"
            },
            "gapStrategy": gap,
            "aggregation": aggregation
        }
        if not isinstance(gap, dict):
            del data['gapStrategy']
        url = f'{self.api}/backend/rest/numberevents/_datehistogramtimeline'
        log.debug('data for _datehistogramtimeline %s', data)
        return self.url(url=url, data=data)

    ### endpoint handlers ###
    def get_numberevents(self, item, size=None, date=None, order='DESC'):
        """
        last 100 (size) events for item in {datetime:value} format
        starts at current timestamp (or date) and returns in time (or goes in future with order 'ASC')
        date:
            if date == None, the time is set to now # default behaviour
            if date == False, the time is discarded from the filter

        """

        items = item if isinstance(item, list) else [item]
        item_keys = list({i.key if isinstance(i, Entity) else i for i in items})
        indexset_keys = list({i.indexset if isinstance(i, Entity) else self.indexset_active.key for i in items})
        log.debug('get numberevents for in indexset %s items %s ', indexset_keys, item_keys)
        filters = [{
            "type": "eventitemid",
            "values": item_keys,
            "invertFilter": False,
            "operator": "or"
        }]
        dt = date if isinstance(date, datetime.datetime) else self.now
        order = self._data_sort(order)
        ts = self._data_timestamp(dt)
        if date is not False:
            if order == 'DESC':
                f_time = {  # added to return only historical events.
                    "type": "range",
                    "to": ts,
                    "maxInclusive": True
                }
                filters.append(f_time)
            elif order == 'ASC':
                f_time = {  # added to return only future events.
                    "type": "range",
                    "from": ts,
                    "minInclusive": True
                }
                filters.append(f_time)
        indexsets = indexset_keys
        data = self._numberevents(indexsets=indexsets, filters=filters, size=size, order=order)
        if data:
            for i in data:
                yield Numberevent(datamodel=i)

    def get_numberevent_first(self, item):
        for e in self.get_numberevents(
            item=item,
            size=1,
            date=False,
            order='ASC'):
            return e

    def get_numberevent_last(self, item):
        for e in self.get_numberevents(
            item=item,
            size=1,
            date=False,
            order='DESC'):
            return e

    def get_numberevent_recent(self, item):
        for e in self.get_numberevents(
            item=item,
            size=1,
            date=None,
            order='DESC'):
            return e

    def get_numberevents_around(self, item, date=None, size=None):
        """eg retrieve 100 around a certain timestamp """
        if isinstance(size, int):
            size = size // 2
        for event in chain(
            self.get_numberevents(item=item, size=size, date=date, order='ASC'),
            self.get_numberevents(item=item, size=size, date=date, order='DESC')
        ):
            yield event

    def get_numberevents_dict(self, item, size):
        return {e.datetime: e.value for e in self.get_numberevents(item=item, size=size)}

    def get_numberevents_dates(self, item, from_date=None, to_date=None, extend=None, order=None):
        """
        retrieve events for item as Numberevent() between two points in time
        :param item: entity of type item
        :param from_date: datetime to start events from (inclusive)
        :param to_date: datetime to stop events till (exclusive)
        :param extend: bool, add one more event before the from_date
        :return:
        """

        if not isinstance(from_date, datetime.datetime):
            from_date = self.now
        if not isinstance(to_date, datetime.datetime):
            to_date = self.now
        if order == 'ASC':
            log.warning('ASC sorting not allowed for get_numberevents_dates !')

        order = 'DESC'  # self._data_sort(order)  # attention, must be 'DESC'
        items = item if isinstance(item, list) else [item]
        item_keys = list({i.key if isinstance(i, Entity) else i for i in items})
        indexset_keys = self._data_indexsets(items)
        f_item = {
            "type": "eventitemid",
            "values": item_keys,
            "invertFilter": False,
            "operator": "or"
        }
        f_range = {
            "type": "range",
            "to": self._data_timestamp(max(from_date, to_date)),
            "maxInclusive": False
        }
        if not extend:
            f_range.update({
                "from": self._data_timestamp(min(from_date, to_date)),
                "minInclusive": True
            })
        while True:
            data = self._numberevents(indexsets=indexset_keys, order=order, filters=[f_item, f_range])
            if data:
                for i in data:
                    event = Numberevent(datamodel=i)
                    yield event
                    if extend and event.datetime < min(from_date, to_date):
                        return
                f_range.update({
                    "to": self._data_timestamp(event.datetime),  # this is why we must have sorting to DESC
                    "maxInclusive": False
                })
            else:
                break

    def get_numberevent_keys(self, keys, indexset=None):
        """
        retrieve a single event using the eventid-filter
        :param keys:
        :param indexset:
        :return:
        """
        f = {
            "type": "eventid",
            "values": keys,
            "invertFilter": False,
            "operator": "or"
        }
        data = self._numberevents(indexsets=indexset, filters=[f], size=len(keys), deleted=False)
        if isinstance(data, list):
            if len(data) != len(keys):
                data_deleted = self._numberevents(indexsets=indexset, filters=[f], size=len(keys), deleted=True)
                if isinstance(data_deleted, list):
                    data.extend(data_deleted)
            r = [Numberevent(datamodel=i) for i in data]
            return r

    def get_numberevent_key(self, key, indexset=None):
        """
        retrieve a single event using the eventid-filter
        :param key:
        :param indexset:
        :return:
        """
        r = self.get_numberevent_keys([key], indexset=indexset)
        if isinstance(r, list) and len(r):
            return r[0]

    def get_aggregation_dates(self, item, aggrs, interval, from_date, to_date, push=None, zero=None):
        """
        retrieve x aggregated buckets of data, including current bucket
        :param item:
        :param aggrs: (list of) aggregation(s) ['avg']
        :param interval: bucket size '15m'
        :param from_date: starting datetime
        :param to_date: ending datetime
        :param push: boolean to set gap strategy 'push' with extended timeline
        :param zero: True excludes 0.0 values; False only used 0.0 values; None includes all values
        :return:
        """
        aggrs = aggrs if isinstance(aggrs, list) else [aggrs]
        gap = {"type": "push", "extendTimeline": True} if bool(push) else None
        zerofilter = [{
            "type": "range",
            "name": "numberValue",
            "from": 0.0,
            "minInclusive": True,
            "to": 0.0,
            "maxInclusive": True,
            "invertFilter": bool(zero)
        }] if bool(zero) else None
        data = self._datehistogramtimeline(
            items=item,
            aggrs=aggrs,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
            gap=gap,
            filters=zerofilter
        )
        if data:
            log.debug('timings from _datehistogramtimeline: %s', {k: v for k, v in data.items() if 'Time' in k})
            buckets = data.get('data')
            if isinstance(buckets, list):
                for i in buckets:
                    ts = i.get('time')
                    if ts:
                        dt = datetime.datetime.fromtimestamp(ts / 1000, tz=datetime.timezone.utc)
                        # using .replace(tzinfo=utc) introduces an error due to fromtimestamp converting to local tz
                        bucket = {
                            'time': dt,
                            'count': i.get('count', 0)
                        }
                        bucket.update(i.get('values', {}))
                        yield bucket

    def get_aggregation_size(self, item, aggrs, interval, size, push=None):
        """
        retrieve x aggregated buckets of data, including current bucket
        :param item:
        :param aggrs: (list of) aggregation(s) ['avg']
        :param interval: bucket size '15m'
        :param size: number of buckets
        :param push: boolean to set gap strategy 'push' with extended timeline
        :return:
        """
        agg_intervals = {
            '1m': datetime.timedelta(minutes=1),
            '5m': datetime.timedelta(minutes=5),
            '15m': datetime.timedelta(minutes=15),
            '1h': datetime.timedelta(hours=1),
            '1d': datetime.timedelta(hours=24),
            # '1M': None  # todo
        }

        end = self.now
        if interval not in agg_intervals:
            raise ValueError('unsupported interval')
        interval_dt = agg_intervals[interval]
        end_rounded = end - datetime.timedelta(seconds=(end.timestamp() % interval_dt.total_seconds()))
        start_rounded = end_rounded - (interval_dt * (size - 1))
        for bucket in self.get_aggregation_dates(
            item=item,
            aggrs=aggrs,
            interval=interval,
            from_date=start_rounded,
            to_date=end,
            push=push
        ):
            yield bucket

    def query(self, query, keys):
        """
        Query a nuql expression and extract the entities for the requested variable
        note behaviour on result:
          keys = 'x' > result = {entities_for_x} ;
          keys = ['x'] > result = {'x': {entities_for_x}}
          keys = ['x','y'] > result = {'x': {entities_for_x}, 'y': {entities_for_y}}
        careful for large requests, use limit and offset is advised
        # consider improvement to change behaviour ['x','y'] > ({entities_for_x}, {entities_for_y})
        :param query: [] of lines for graphql
        :param keys: the [] of str variable(s)
        :return: {variable: {entityKey: Entity}} or {entityKey: Entity}
        """
        result = {}
        result_with_keys = isinstance(keys, list)
        data = self._graphql(query)
        if data:
            log.debug('time _graphql %sms', data.get('time'))
            variables = data.get('variables', {})
            nodes = data.get('nodes', {})
            for k in keys if result_with_keys else [keys]:
                result.update({k: {}})
                for entityKey in variables.get(f"?{k}", []):
                    e = nodes.get(entityKey, {})
                    result[k].update({entityKey: Entity(datamodel=e, indexsets=self.indexsets)})
        return result if result_with_keys else result.get(keys)

    def fix_kwargs(self, kwargs):
        """
        map python styled arguments like external_id to byneuron style externalId
        :param kwargs:
        :return:
        """
        # rename_kwarg = {'external_id': 'externalId', 'public_id': 'publicId', 'codetype': 'codeType'}
        for k, v in kwargs.copy().items():
            if k.count('_'):
                words = k.split('_')
                new_key = words[0] + ''.join(w.capitalize() for w in words[1:])
                kwargs.update({new_key: v})
        return kwargs

    def get_entities(self, entitytype, indexset=None, **kwargs):
        """
        iterates entities using a filter e.g. get_entities('Item', 'hydrobox', 'externalId':'regex:0/1/.*'}
        constructs the required nuql query
        :param entitytype: eg Item, Device, ..
        :param indexset:
            True, search all indexSets;
            None, search selected indexSet;
            string or [str], search indexSets by attribute-name
        :param kwargs:
            k:
                'key' -> entity's key
                'name', 'externalId', 'publicId', 'codeType' - > entity's attributes
                'implementation' -> link:isImplementationOf Definition; to be paired with the externalId
                'member' -> link:isMemberOf Gateway
                'source', 'target' -> link:hasTarget, link:hasSource
                'role', 'type' -> case deviceRole, itemType, to be paired with string (e.g. DEFAULT for deviceRole#DEFAULT)
            v:
                True -> any
                None -> none
                [] -> []
                'regex:?' - regex:'?'

        """

        def from_kwarg(kwarg_key):
            v = kwargs.get(kwarg_key)
            if isinstance(v, str):
                return f'regex:"{v[6:]}"' if v.startswith('regex:') else f'"{v}"'
            elif isinstance(v, list):
                return f'{[i for i in v]}'
            elif v is True:
                return f'value:any'
            elif v is None:
                return f'value:none'

        entity_list = self._data_indexsets(indexset)
        query = [
            f"IndexSet:?indexSet entity:key {entity_list}.",
            f"{entitytype}:?e link:{'isAssignedTo' if entitytype == 'Gateway' else 'isDefinedIn'} ?indexSet."
        ]
        filter_list = []
        # fix format used in Entity to that of datamodel
        kwargs = self.fix_kwargs(kwargs)
        for k in ['key']:
            if k in kwargs:
                filter_list.append(f'entity:{k} {from_kwarg(k)}')
        for k in ['name', 'externalId', 'publicId', 'codeType']:
            if k in kwargs:
                filter_list.append(f'attribute:{k} {from_kwarg(k)}')
        for k in ['type', 'role']:
            if k in kwargs:
                a = f'{entitytype.lower()}{k[0].upper()}{k[1:].lower()}'
                filter_list.append(f'attribute:{a} "{a}#{kwargs.get(k)}"')
        for k in ['implementation']:
            if k in kwargs:
                v = kwargs.get(k)
                if isinstance(v, Entity):
                    query.append(f'{v.entity_type}:?d link:isDefinedIn ?indexSet; entity:key {v.key}.')
                elif isinstance(v, str):
                    query.append(
                        f'{entitytype}Definition:?d link:isDefinedIn ?indexSet; attribute:externalId {from_kwarg(k)}.')
                else:
                    continue
                filter_list.append(f'link:isImplementationOf ?d')
        for k in ['member']:
            if k in kwargs:
                v = kwargs.get(k)
                if isinstance(v, Entity):
                    query.append(f'{entitytype}:?g link:isAssignedTo IndexSet:?is; entity:key {v.key}.')
                elif isinstance(v, str):
                    query.append(f'Gateway:?g link:isAssignedTo IndexSet:?is; attribute:externalId {from_kwarg(k)}.')
                else:
                    continue
                filter_list.append(f'link:isMemberOf ?g')
        for k in ['source', 'target']:
            if k in kwargs:
                v = kwargs.get(k)
                if not isinstance(v, Entity):
                    continue
                query.append(f'{v.entity_type}:?r{k} link:isDefinedIn IndexSet:?is; entity:key {v.key}.')
                relation_type = f'{v.entity_type}{entitytype}Relation' if k == 'source' else \
                    f'{entitytype}{v.entity_type}Relation'
                link1 = f'link:has{k.capitalize()} {v.entity_type}:?r{k}'
                link2 = f'link:has{"Target" if k == "source" else "Source"} {entitytype}:?related'
                query.append(f'{relation_type}:?r link:isDefinedIn IndexSet:?is; {link1}; {link2}.')
                query.append(f'{entitytype}:?e intersection ?related.')
        if filter_list:
            query.append(f"{entitytype}:?e {'; '.join(filter_list)}.")

        offset, limit = 0, 20
        while True:
            query.append(f"{entitytype}:?e sort+ entity:key; limit {limit}; offset {offset}.")
            log.debug('nuql query %s', query)
            entities = self.query(query, 'e')
            log.debug('nuql query returned %s entities', len(entities))
            for e in entities.values():
                if isinstance(e, Entity):
                    yield e
            if len(entities) < limit:
                break
            query.pop()  # remove limit
            offset += limit

    # DeviceDeviceRelation:?result link:isDefinedIn #IndexSet:?index. DeviceDeviceRelation:?result link:hasTarget Device:?deviceTarget. DeviceDeviceRelation:?result link:hasSource Device:?deviceSource. DeviceDeviceRelation:?result sort+ entity:key; limit 15; offset 15.

    def get_entity(self, entitytype, **kwargs):
        for i in self.get_entities(entitytype, **kwargs):
            return i

    def get_indexsets(self):
        q = ['IndexSet:?indexSet attribute:name value:any.']
        r = self.query(q, 'indexSet')
        return [e for e in r.values() if isinstance(e, Entity)]

    def datamodel(self, data):
        """
        attention this is an iterator
        :param data: (list with ) Numberevent, Entity
        :return: yields the datamodel objects
        """

        data = self._graphmodel(data)
        if data:
            log.debug('graphmodel returned %s', data)
            for k, v in data.get('result', {}).items():
                events = v.get('events', [])
                nodes = v.get('nodes', {})
                if k == 'entityDataModel':
                    for i in nodes.values():
                        yield Entity(datamodel=i, indexsets=self.indexsets)
                elif k == 'numberEventDataModel':
                    for i in events:
                        yield Numberevent(datamodel=i)

    def create_entity(self, entity):
        log.info('create_entity %s', entity)
        entity.set_context('create')
        log.debug('create_entity %s %s %s', entity.entity_type, entity.role, entity.type)
        if entity.entity_type in ['Device', 'Item', 'Place', 'Dashboard']:
            # indexSetCode only for entity that are defined in indexSet
            if entity.role:
                for role in entity.role:
                    self.set_isc(f'{entity.entity_type.lower()}Role', role)
            if entity.type:
                self.set_isc(f'{entity.entity_type.lower()}Type', entity.type)
        log.debug('create_entity %s', json.dumps(entity.wrap(), indent=2))
        for i in self.datamodel(entity):
            if i.key == entity.key:
                log.info('created entity %s', i)
                return i

    def update_entity(self, entity):
        if isinstance(entity, Entity):
            for i in self.update(entity):
                return i

    def delete_entity(self, entity, undo=False):
        if isinstance(entity, Entity):
            for i in self.update(entity, delete=not undo):
                return i

    def update_event(self, event):
        if isinstance(event, Numberevent):
            for i in self.update(event):
                return i

    def delete_event(self, event, undo=False):
        if isinstance(event, Numberevent):
            for i in self.update(event, delete=not undo):
                return i

    def update(self, datamodel, delete=None):
        datamodels = datamodel if isinstance(datamodel, list) else [datamodel]
        for d in datamodels:
            if isinstance(d, (Numberevent, Entity)):
                if delete is True:
                    d.set_context('delete')  # <- method to delete;
                    # d._datamodel.update({'deleted': True})  # <- does not work!
                elif delete is False:
                    d.set_context('undelete')
                    # d._datamodel.update({'deleted': False})  # method to undo deletion
                else:
                    d.set_context('update')
        return [i for i in self.datamodel(datamodels)]

    def create_from_definition(self, definition, inputs):

        api_endpoint = {
            'DeviceDefinition': 'asset',
            'PlaceDefinition': 'site',
            'ItemDefinition': 'timeseries'
        }
        if isinstance(definition, Entity) and definition.entity_type in api_endpoint:
            for i in self._openapi(
                endpoint=api_endpoint.get(definition.entity_type),
                action='POST',
                data={
                    "definition": {
                        "identification": {
                            "id": f"{definition.key}"
                        },
                        "inputs": inputs
                    }
                }
            ):
                return i

        def runDefinition(self, entityAPItype, id, inputs: dict):
            '''
            returns id for created entity
            entityAPItype : eg 'assets' for device
            id: the definition's key
            inputs: eg {
                "gateway": [
                    {
                        "id": "f7cbd450-3942-11ef-b828-37fd3bda07f4"
                    }
                ],
                "meter": null,
                "iName": "test",
                "iPmax": "20",
                "iPscale": "0.001",
                "iEscale": "0.001"
            }
            '''
            result = ''
            url = '{}/api/v1/{}/{}'.format(self.baseUrl, self.tenant, entityAPItype)
            pld = {
                "definition": {
                    "identification": {
                        "id": "{}".format(id)
                    },
                    "inputs": inputs
                }
            }
            r = self.requestUrl(url=url, pld=pld)

            if r:
                log.info("runDefinition %s", r)
                result = r[0]['identification']['id']
            return result

    def create_item(self, **kwargs):
        kwargs = self.fix_kwargs(kwargs)
        # to filter the keywords we can allow, and to set required fields
        item_config = {
            'description': kwargs.get('description'),
            'name': kwargs.get('name'),
            'externalId': kwargs.get('externalId'),
            'publicId': self._publicid(entitytype="Item"),
            'active': True,
            'valid': True,
            'valueType': 'Double',
            'unit': kwargs.get('unit'),  # optional
            'data': kwargs.get('data'),  # optional
            'metaKeywords': kwargs.get('metaKeywords'),  # optional
            'metaBooleans': kwargs.get('metaBooleans'),  # optional
            'metaValues': kwargs.get('metaValues'),  # optional
            'roles': kwargs.get('roles', ['DEFAULT']),
            'type': kwargs.get('type', 'DEFAULT')
        }
        e = Entity().create('Item', self.indexset_active, **{k: v for k, v in item_config.items() if v is not None})
        if kwargs.get('definition'):
            v = kwargs.get('definition')
            if isinstance(v, str):
                e = self.set_definition(e, definition=None, externalId=v)
            elif isinstance(v, Entity):
                e = self.set_definition(e, definition=v)
        return self.create_entity(e)

    def create_device(self, **kwargs):
        kwargs = self.fix_kwargs(kwargs)
        device_config = {
            'description': kwargs.get('description'),
            'name': kwargs.get('name'),
            'externalId': kwargs.get('externalId'),
            'publicId': self._publicid(entitytype="Device"),
            'active': True,
            'valid': True,
            'data': kwargs.get('data'),  # optional
            'metaKeywords': kwargs.get('metaKeywords'),  # optional
            'metaBooleans': kwargs.get('metaBooleans'),  # optional
            'metaValues': kwargs.get('metaValues'),  # optional
            'roles': kwargs.get('roles', ['DEFAULT']),
            'type': kwargs.get('type', 'DEFAULT')
        }
        e = Entity().create('Device', self.indexset_active, **{k: v for k, v in device_config.items() if v is not None})
        if kwargs.get('definition'):
            v = kwargs.get('definition')
            if isinstance(v, str):
                e = self.set_definition(e, definition=None, externalId=v)
            elif isinstance(v, Entity):
                e = self.set_definition(e, definition=v)
        if kwargs.get('gateway'):
            v = kwargs.get('gateway')
            if isinstance(v, Entity) and v.type == 'Gateway':
                e.set_link('isMemberOf', v)
                log.debug('set isMemberOf', e)
                # optional set type to 'GATWEWAY' for compability with frontend

        # todo add profile, assetModel, status
        return self.create_entity(e)

    def create_gateway(self, **kwargs):
        kwargs = self.fix_kwargs(kwargs)
        device_config = {
            'description': kwargs.get('description'),
            'name': kwargs.get('name'),
            'externalId': kwargs.get('externalId'),
            'active': True,
            # 'valid': True,
            'data': kwargs.get('data'),  # optional
            'metaKeywords': kwargs.get('metaKeywords'),  # optional
            'metaBooleans': kwargs.get('metaBooleans'),  # optional
            'metaValues': kwargs.get('metaValues'),  # optional
            # 'roles': kwargs.get('roles', []),
            # 'type': kwargs.get('type', 'DEFAULT'),
            'code': kwargs.get('type')  # eg BYNODE
        }
        e = Entity().create('Gateway', self.indexset_active,
                            **{k: v for k, v in device_config.items() if v is not None})
        return self.create_entity(e)

    def create_place(self, **kwargs):
        kwargs = self.fix_kwargs(kwargs)
        place_config = {
            'description': kwargs.get('description'),
            'name': kwargs.get('name'),
            'externalId': kwargs.get('externalId'),
            'publicId': self._publicid(entitytype="Place"),
            'active': True,
            'valid': True,
            'data': kwargs.get('data'),  # optional
            'metaKeywords': kwargs.get('metaKeywords'),  # optional
            'metaBooleans': kwargs.get('metaBooleans'),  # optional
            'metaValues': kwargs.get('metaValues'),  # optional
            'geoLocation': kwargs.get('geoLocation'),
            'roles': kwargs.get('roles', ['DEFAULT']),
            'type': kwargs.get('type', 'DEFAULT')
        }
        e = Entity().create('Place', self.indexset_active, **{k: v for k, v in place_config.items() if v is not None})
        if kwargs.get('definition'):
            v = kwargs.get('definition')
            if isinstance(v, str):
                e = self.set_definition(e, definition=None, externalId=v)
            elif isinstance(v, Entity):
                e = self.set_definition(e, definition=v)

        return self.create_entity(e)

    def create_defition(self, type, external_id, data):
        """
        create a definition
        :param type: e.g. Device, Dashboard, but DashboardDefinition will also pass
        :param external_id: externalId for entity; e.g. MY_DEFINITION_01;  name will be auto created as 'My Definition 01'
        :param data: dict styled definition for the datafield
        :return:
        """
        type = type.split("Definition")[0].title()
        e = Entity().create(
            entitytype=f'{type}Definition',
            indexset=self.indexset_active,
            name=external_id.replace('_', ' ').title(),
            externalId=external_id,
            data=data
        )
        return self.create_entity(e)

    def create_mastercode(self, codetype, code):
        """
        crete a code in the master dataset, e.g. for Gateway -> gatewayType#BYNODE
        :param codetype: e.g. gatewayType
        :param code: e.g. BYNODE
        :return:
        """
        e = Entity().create(entitytype='Code',
                            indexset=None,  # since master index > avoid create indexset relation
                            key=f'{codetype}#{code}',
                            masterCodeType=codetype,
                            masterCode=code)
        return self.create_entity(e)

    def create_code(self, codetype, code):
        """
        create a codeType for a tenant. error 400 - bad request - if exists
        > use set_isc() as entrypoint
        :param codetype:  e.g. itemRole
        :param code: e.g. DEFAULT
        :return:
        """
        e = Entity().create('IndexSetCode',
                            indexset=self.indexset_active,
                            codeType=codetype,
                            code=code,
                            key=f'{codetype}#{code}')
        log.debug('entity builded: %s', e)
        return self.create_entity(e)

    def create_codetype(self, codetype, parent_codetype=None):
        """
        create a codeType for a tenant. error 400 - bad request - if exists
        > use set_isc() as entrypoint
        :param codetype: 'itemRole'
        :param parent_codetype: 'reference-data'
        :return:
        """
        e = Entity().create('IndexSetCodeType', self.indexset_active, key=codetype)
        if parent_codetype:
            pct = self.get_entity('IndexSetCodeType', key=parent_codetype)
            if isinstance(pct, Entity):
                e.set_link('hasParent', pct)
        return self.create_entity(e)

    def create_relation(self, target, source, **kwargs):
        if not isinstance(target, Entity):
            return
        if not isinstance(source, Entity):
            return
        kwargs = self.fix_kwargs(kwargs)
        config = {  # OPTIONAL
            'active': kwargs.get('active'),
            'fromDate': kwargs.get('fromDate'),
            'toDate': kwargs.get('toDate'),
            'data': kwargs.get('data'),
            'metaKeywords': kwargs.get('metaKeywords'),
            'metaBooleans': kwargs.get('metaBooleans'),
            'metaValues': kwargs.get('metaValues')
        }

        if not source.roles:
            source.set_attribute('roles', ['DEFAULT'])
            source = self.update_entity(source)
            if not source:
                return
        if not target.roles:
            target.set_attribute('roles', ['DEFAULT'])
            target = self.update_entity(target)
            if not source:
                return
        relation_type = f'{source.entity_type}{target.entity_type}Relation'
        source_role = source.roles[0]
        source_role_label = f'{source.entity_type.lower()}Role'
        source_role_full = f'{source_role_label}#{source_role}'
        target_role = target.roles[0]
        target_role_label = f'{target.entity_type.lower()}Role'
        target_role_full = f'{target_role_label}#{target_role}'
        force_key = '#'.join([source.key, target.key, source_role_full, target_role_full])
        e = Entity().create(
            relation_type,
            self.indexset_active,
            key=force_key,
            **{k: v for k, v in config.items() if v is not None}
        )
        e.set_link('hasSource', source)
        e.set_link('hasTarget', target)

        return self.create_entity(e)

    def set_features(self, parent, children):
        """
        :param parent: Entity of type Device, Site to create hasFeature-relation in
        :param children: [] of Entity of type Item to create hasFeature-relation to
        :return: parent after update
        """
        for child in children:
            parent.set_link('hasFeature', child)
        return self.update_entity(parent)

    def remove_features(self, parent, children, delete_childeren=False):
        """
        :param parent: Entity of type Device, Site to remove hasFeature-relation from
        :param children: [] of Entity of type Item to be removed hasFeature-relation
        :return: parent after update
        """
        for child in children:
            parent.del_link(child)
        parent = self.update_entity(parent)
        if delete_childeren:
            for child in children:
                self.delete_entity(child)
        return parent

    def duplicate(self, entity, indexset):
        return self.copy_to_indexset(entity, indexset)

    def copy_to_indexset(self, entity, indexset):
        """
        duplicate an entity to a different indexSet
        :param entity: Entity to copy
        :param indexset: indexSet (Entity) to copy to
        :return:
        """
        e = Entity().create(
            entity.entity_type,
            indexset,
            description=entity.description,
            name=entity.name,
            externalId=entity.external_id,
            data=entity.data,
            metaKeywords=entity.meta_keywords,
            metaBooleans=entity.meta_booleans)
        log.info('new entity %s from copy %s', e, entity)
        return self.create_entity(e)

    def copy_entity(self, entitytype, externalId):
        """
        copy entity with entityTpe and matching externalId to the active indexset
        :param entitytype:
        :param externalId:
        :return:
        """
        # test if not local
        entities = [e for e in self.get_entities(entitytype, indexset=True, externalId=externalId)]
        log.debug('copy_entity - found %s matching entities', len(entities))
        if not entities:
            return
        local_indexset = self.indexset_active
        for e in entities:
            if e.indexset == local_indexset.key:
                log.debug('copy_entity - exist in local - skip')
                return e
        remote_entity = entities[0]  # first pick
        if isinstance(remote_entity, Entity):
            log.debug('duplicate %s to %s', remote_entity, local_indexset)
            local = self.copy_to_indexset(remote_entity, local_indexset)
            return local

    def set_definition(self, entity, definition, **kwargs):
        if not isinstance(entity, Entity):
            return
        definition_type = f'{entity.entity_type}Definition'
        definition_local = None
        if definition is None:
            definition = self.get_entity(definition_type, **kwargs)
        if isinstance(definition, Entity) and definition.entity_type == definition_type:
            if definition.indexset == self.indexset_active:
                definition_local = definition
            else:
                definition_local = self.copy_to_indexset(definition, self.indexset_active)
        if definition_local:
            entity = entity.set_link('isImplementationOf', definition_local)
        return entity

    def set_isc(self, codetype, code):
        """
        routine to make sure codetypes#code are available in entity creation
        buffers codes per codetype
        todo create codetype relation to root > reference-data
        :param codetype: eg itemRole
        :param code: eg DEFAULT
        :return:
        """

        log.debug('set_isc for %s#%s', codetype, code)
        if self._isc is None:
            self._isc = {}
        if self.indexset_active != self._isc.get('indexSet'):
            log.debug('set_isc > initiate indexSetBuffer')
            self._isc = {'indexSet': self.indexset_active}
            for e in self.get_entities('IndexSetCodeType'):
                self._isc.update({e.key: None})
            log.debug('initiate indexSetBuffer: %s', self._isc)
        if codetype not in self._isc:
            log.debug('set_isc > create_codetype %s', codetype)
            self.create_codetype(codetype, 'reference-data')
            self._isc.update({codetype: None})
            # create codetype
            # buffer the code e.g. DEFAULT for the codetype e.g. itemRole
        if not self._isc.get(codetype):
            log.debug('set_isc > load existing codes on %s', codetype)
            # buffer existing codes
            existing_codes = [e.code for e in self.get_entities('IndexSetCode', codeType=codetype)]
            self._isc.update({codetype: existing_codes})
            log.debug('load indexSetBuffer for %s: %s', codetype, existing_codes)
        if code not in self._isc.get(codetype, []):
            log.debug('set_isc > create code %s#%s', codetype, code)
            self.create_code(codetype, code)
            self._isc[codetype].append(code)
            # create code

        log.debug('buffered indexSetCodetypes %s', self._isc)
        # buffer existing codes


class Entity:
    def __init__(self, datamodel=None, indexsets=None, openapi=None):
        self._datamodel = datamodel if isinstance(datamodel, dict) else {}
        self._indexsets = indexsets if isinstance(indexsets, list) else []
        self._openapi = openapi if isinstance(openapi, dict) else {}

    def __repr__(self):
        r = [self.entity_type, self.indexset_name, self.public_id, self.name]
        return ' '.join([i for i in r if i != None])

    def wrap(self):
        return self._datamodel

    def _prop(self, key):
        return self._datamodel.get(key)

    def _attr(self, name):
        for a in self._datamodel.get('attributes', []):
            if a.get('name') == name:
                for k in a:
                    if k.endswith('Value') or k.endswith('Values'):
                        return a.get(k)

    def _link(self, linktype):
        for link in self._links(linktype):
            return link

    def _links(self, linktype):
        for link in self._datamodel.get('links', []):
            if link.get('linkType') == linktype or link.get('label') == linktype:
                yield link.get('entityKey')

    @staticmethod
    def tail(s):
        seperator = ['#', '.']
        if isinstance(s, str):
            for i in seperator:
                if s.count(i):
                    return s.split(i)[-1]

    @property
    def key(self):
        return self._prop('key')

    @property
    def id(self):
        return self._prop('id')

    @property
    def entity_type(self):
        return self.tail(self._prop('type'))

    @property
    def entity_type_ref(self):
        # for publicId
        return self.tail(self._attr('entityTypeRef'))

    @property
    def entity_type_long(self):
        return self._prop('type')

    @property
    def description(self):
        return self._prop('description')

    @property
    def deleted(self):
        return self._prop('deleted')

    @property
    def name(self):
        return self._attr('name')

    @property
    def external_id(self):
        return self._attr('externalId')

    @property
    def public_id(self):
        return self._attr('publicId')

    @property
    def unit(self):
        return self._attr('unit')

    @property
    def active(self):
        return self._attr('active')

    @property
    def codetype(self):  # for indexSetCode
        return self._attr('codeType')

    @property
    def code(self):  # for indexSetCode
        return self._attr('code')

    @property
    def data(self):
        data = self._attr('data')
        if data is not None:
            try:
                return json.loads(data)
            except json.JSONDecoder:
                log.exception('decode error on entity data')
            except TypeError:
                log.exception('type error on entity data')

    def set_data(self, data):
        self.update(data=data)

    @property
    def from_date(self):
        date = self._attr('fromDate')
        if date is not None:
            return datetime.datetime.fromisoformat(date).replace(tzinfo=datetime.timezone.utc)

    def set_from_date(self, data):
        self.update(fromDate=data)

    @property
    def to_date(self):
        date = self._attr('toDate')
        if date is not None:
            return datetime.datetime.fromisoformat(date).replace(tzinfo=datetime.timezone.utc)

    def set_to_date(self, data):
        self.update(toDate=data)

    @property
    def meta_indexset_codes(self):
        meta = self._attr('metaIndexSetCodes')
        if meta:
            return {i.get('key'): i.get('value') for i in meta}

    def set_meta_indexset_codes(self, data):
        if isinstance(data, dict):
            d = self.meta_indexset_codes or {}
            d.update(data)
            self.update(metaIndexSetCodes=data)

    @property
    def meta_keywords(self):
        meta = self._attr('metaKeywords')
        if isinstance(meta, list):
            return {i.get('key'): i.get('value') for i in meta}

    def set_meta_keywords(self, data):
        if isinstance(data, dict):
            d = self.meta_keywords or {}
            d.update(data)
            self.update(metaKeywords=data)

    @property
    def meta_booleans(self):
        meta = self._attr('metaBooleans')
        if isinstance(meta, list):
            return {i.get('key'): bool(i.get('value')) for i in meta}

    def set_meta_booleans(self, data):
        if isinstance(data, dict):
            d = self.meta_booleans or {}
            d.update(data)
            self.update(metaBooleans=data)

    @property
    def meta_values(self):
        meta = self._attr('metaValues')
        if isinstance(meta, list):
            return {i.get('key'): i.get('value') for i in meta}

    def set_meta_values(self, data):
        if isinstance(data, dict):
            d = self.meta_values or {}
            d.update(data)
            self.update(metaValues=d)

    @property
    def geo_location(self):
        meta = self._attr('geoLocation')
        if isinstance(meta, dict):
            return (meta.get('lat'), meta.get('lon'))

    def set_geo_location(self, data):
        self.update(geoLocation=data)

    @property
    def role(self):
        roles = self._attr(f'{self.entity_type.lower()}Role')
        if isinstance(roles, list):
            return [self.tail(i) for i in roles]
        return []

    @property
    def roles(self):
        return self.role

    @property
    def type(self):
        t = self._attr(f'{self.entity_type.lower()}Type')
        if t:
            return self.tail(t)

    @property
    def indexset(self):
        if self.entity_type == 'IndexSet':
            return self.key
        if self.entity_type == 'Gateway':
            return self._link('isAssignedTo')
        return self._link('isDefinedIn')

    @property
    def indexset_name(self):
        if self._indexsets:
            key = self.indexset
            for e in self._indexsets:
                if e.key == key:
                    return e.name

    @property
    def profile(self):
        return self._link('hasFeatureProfile')

    @property
    def gateway(self):
        return self._link('isMemberOfGateway')

    @property
    def definition(self):
        return self._link('isImplementationOf')

    @property
    def items(self):
        return [i for i in self._links('hasFeatureItem')]

    @property
    def source(self):
        return self._link('hasSource')

    @property
    def target(self):
        return self._link('hasTarget')

    def create_event(self, value, dt):
        event = Numberevent()
        event.create(value=value, dt=dt, item=self)
        return event

    def create(self, entitytype, indexset, **kwargs):
        new_id = str(uuid.uuid4())
        key = kwargs.get('key', new_id)  # method to overwrite key, eg for indexSetCodeType
        self._datamodel = {
            "type": f'com.bynubian.shared.entities.{entitytype}',
            "id": new_id,
            "key": key,
            "links": [],
            "attributes": []
        }
        log.debug('Entity.create: _datamodel %s', self._datamodel)
        self.set_context('create')
        linktype = 'isAssignedTo' if self.entity_type == 'Gateway' else 'isDefinedIn'
        if isinstance(indexset, Entity) and indexset.entity_type == 'IndexSet':
            self.set_link(linktype, indexset)
            if not indexset in self._indexsets:
                self._indexsets.append(indexset)
        self.update(**kwargs)
        return self

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v is None:
                continue
            elif k in ['description']:
                self._datamodel.update({k: v})
            else:
                self.set_attribute(k, v)

    def set_context(self, action):
        context = self._datamodel.get('entityContext', {})
        context.update({"action": action})
        self._datamodel.update({"entityContext": context})

    def del_link(self, entity):
        """
        remove link with this entity; also works with entity_key
        """
        self.set_link(linktype=None, entity=entity)

    def set_link(self, linktype, entity):
        """
        create/update/delete link with this entity
        :param linktype:
            e.g. hasFeature;
            None -> remove link
        :param entity: Entity;
            in case of remove link this can also be an entity.key
        :return:
        """

        def _index():
            find_key = entity.key if isinstance(entity, Entity) else entity
            for position, _link in enumerate(self._datamodel['links']):
                if _link.get('entityKey') == find_key:
                    return position

        if 'links' not in self._datamodel:
            self._datamodel.update({'links': []})
        i = _index()
        if linktype is None:  # method to remove
            if i is not None:
                self._datamodel['links'].pop(i)
        elif isinstance(entity, Entity) and entity.key:
            log.debug('set_link %s with %s / %s ', linktype, entity, entity.indexset)
            link = {
                "linkType": linktype,  # hasFeature
                "label": f'{linktype}{entity.entity_type}',  # hasFeatureItem
                'entityKey': entity.key,
                'entityId': entity.id,
                'entityType': entity.entity_type_long,
                'entityIndexSetKey': entity._link('isDefinedIn'),
                'entityIndexSetId': entity._link('isDefinedIn')
            }
            link = {k: v for k, v in link.items() if
                    v is not None}  # this will remove entityIndexSetKey for gateway and indexset entities
            if i is None:
                self._datamodel['links'].append(link)
            else:
                self._datamodel['links'][i] = link

    def set_attribute(self, name, value):
        def _index(attr_name):
            for position, _attr in enumerate(self._datamodel.get('attributes', [])):
                if _attr.get('name') == attr_name:
                    return position

        def _attribute(attr_name, attr_value, attr_entity, attr_type):

            attr = {  # , "com.bynubian.shared.Boolean", "numberValue", name, int(bool(value)))
                "name": attr_name,
                "type": f'com.bynubian.shared.{attr_entity}',
                attr_type: attr_value
            }
            log.debug('_attribute %s', attr)
            return attr

        if 'attributes' not in self._datamodel:
            self._datamodel.update({'attributes': []})
        # set value to None to have the attribute deleted
        if value is None:
            i = _index(name)
            if i is not None:
                self._datamodel['attributes'].pop(i)
            return
        try:
            attr = None
            log.debug('set_attribute %s: %s', name, value)
            if name in ['name', 'externalId', 'publicId']:
                attr = _attribute(name, str(value), 'Keyword', 'keywordValue')
            elif name in ['active', 'valid']:
                attr = _attribute(name, int(bool(value)), 'Boolean', 'numberValue')
            elif name in ['valueType']:
                attr = _attribute(name, str(value), 'ValueType', 'keywordValue')
            elif name in ['data']:
                attr = _attribute(name, json.dumps(value), 'Json', 'textValue')
            elif name in ['unit']:
                attr = _attribute(name, str(value), 'Unit', 'keywordValue')
            elif name in ['metaKeywords']:
                list_values = [{'key': k, 'value': str(v)} for k, v in value.items()] \
                    if isinstance(value, dict) else []
                attr = _attribute(name, list_values, 'ExtensionKeyword', 'extensionKeywordValues')
            elif name in ['metaBooleans']:
                list_values = [{'key': k, 'value': int(bool(v))} for k, v in value.items()] \
                    if isinstance(value, dict) else []
                attr = _attribute(name, list_values, 'ExtensionBoolean', 'extensionNumberValues')
            elif name in ['metaValues']:
                list_values = [{'key': k, 'value': float(v)} for k, v in value.items()] \
                    if isinstance(value, dict) else []
                attr = _attribute(name, list_values, 'ExtensionDouble', 'extensionNumberValues')
            elif name in ['geoLocation']:
                values = {"lat": float(value[0]), "lon": float(value[1])} \
                    if isinstance(value, tuple) and len(value) == 2 else {}
                attr = _attribute(name, values, 'GeoPoint', 'geoPointValue')
            elif name in ['codeType']:
                attr = _attribute(name, str(value), 'IndexSetCodeType', 'keywordValue')
            elif name in ['code']:  # e.g. gatewayType#BYNODE
                if self.entity_type == 'IndexSetCode':
                    attr = _attribute(name, value, 'Code', 'keywordValue')
                else:
                    # gatewayType#BYNODE
                    name = f'{self.entity_type.lower()}Type'
                    this_value = f'{name}#{value}'  # gatewayType#BYNODE
                    attr = _attribute(name, this_value, 'Code', 'keywordValue')
            elif name in ['masterCode']:  # e.g. gatewayType
                attr = _attribute('code', value, 'Keyword', 'keywordValue')
            elif name in ['masterCodeType']:  # e.g. gatewayType
                attr = _attribute('codeType', value, 'CodeType', 'keywordValue')
            elif name.endswith('Role'):
                # this is used in relations with single roles
                # e.g. name itemRole, value DEFAULT
                attr = _attribute(name, f'{name}#{value}', 'IndexSetCode', 'keywordValue')
            elif name in ['roles']:
                name = f'{self.entity_type.lower()}Role'
                list_roles = [f'{name}#{role}' for role in value]
                attr = _attribute(name, list_roles, 'IndexSetCode', 'keywordValues')
            elif name in ['type']:
                name = f'{self.entity_type.lower()}Type'
                type_value = f'{name}#{value}'
                attr = _attribute(name, type_value, 'IndexSetCode', 'keywordValue')

            elif name in ['fromDate', 'toDate']:
                isodate = None
                if value is None:
                    isodate = datetime.date.today().isoformat() if name == 'fromDate' else "9999-12-31"
                elif isinstance(value, str):
                    try:
                        datetime.date.fromisoformat(value)
                        isodate = value
                    except ValueError:
                        return
                elif isinstance(value, datetime.date):
                    isodate = value.isoformat()
                elif isinstance(value, datetime.datetime):
                    isodate = value.date().isoformat()
                if isodate:
                    attr = _attribute(name, isodate, 'Date', 'dateValue')
            else:
                return
            if attr is None:
                return
            i = _index(name)
            if i is None:
                self._datamodel['attributes'].append(attr)
            else:
                self._datamodel['attributes'][i] = attr

        except (Exception,):
            log.exception('set_attribute')

    """
    # idea to allow event creation directly from entity
    def set_event(self, val, dt=None):
        #test if byneuron is defined
        #test if entity is Item
        if dt is None:
            dt = self.bn.now
        event = Numberevent()
        event.create(value=val, dt=dt, item=self)
        self.bn.graphmodel(numberEvents=[event])
    """


class Numberevent:

    def __init__(self, datamodel=None):
        self._datamodel = datamodel if isinstance(datamodel, dict) else {}

    def __repr__(self):
        return f'Numberevent {self.datetime} {self.value}{", " + str(self.tags) if self.tags else ""}{", deleted" if self.deleted else ""}'

    def wrap(self):
        return self._datamodel

    def create(self, value, dt, item):
        """
        create the required attributes to populate the Event
        :param value: the numberValue that will be floated
        :param dt: datetime, either tz-aware or utc
        :param item: the Item-entity to link the event with
        :return:
        """

        def timestamp(dt):
            # if not timezone aware; force UTC
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            dt_utc = dt.astimezone(datetime.timezone.utc)
            return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # microseconds truncated to milliseconds

        datamodel = {
            "timestamp": timestamp(dt),
            "id": str(uuid.uuid4()),  # todo is this needed
            "itemId": item.key,
            "documentType": "NumberEvent",
            "eventContext": {
                "action": "create"
            },
            "indexSetKey": item.indexset,
            "numberValue": float(value)
        }
        self._datamodel = datamodel

    def set_value(self, value):
        if value != value:
            # check for nan
            pass
        elif isinstance(value, (float, int, bool)):
            self._datamodel.update({"numberValue": float(value)})

    def set_context(self, action):
        context = self._datamodel.get('eventContext', {})
        context.update({"action": action})
        self._datamodel.update({"eventContext": context})

    def set_tag(self, tag):
        if 'tags' not in self._datamodel:
            self._datamodel.update({'tags': [tag]})
        elif tag not in self.tags:
            self._datamodel['tags'].append(tag)
        return self

    @staticmethod
    def to_datetime(timestamp):
        if timestamp is not None:
            return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')

    @property
    def datetime(self):
        return self.to_datetime(self._datamodel.get('timestamp'))

    @property
    def value(self):
        value = self._datamodel.get('numberValue')
        if value is not None:
            return value  # float(value)

    @property
    def now(self):
        """timezone aware utc now"""
        return datetime.datetime.now(datetime.timezone.utc)

    @property
    def deleted(self):
        return self._datamodel.get('deleted')

    @property
    def id(self):  # this is the id of the event
        return self._datamodel.get('id')

    @property
    def item_id(self):  # this is the id of the item linking to this event
        return self._datamodel.get('itemId')

    @property
    def tags(self):
        return self._datamodel.get('tags', [])

    @property
    def dates(self):
        dates = self._datamodel.get('dates')
        if dates is not None:
            return {i.get('type'): self.to_datetime(i.get('timestamp')) for i in dates}
        return {}

    @property
    def datetime_created(self):
        return self.dates.get('byneuronCreated')

    @property
    def datetime_updated(self):
        return self.dates.get('byneuronUpdated')


def example01():
    logging.basicConfig(level=logging.INFO)
    log.info('list tenants')
    # list tenants
    with Byneuron() as r:
        print(f'IndexSets in this environment: {[e.name for e in r.indexsets]}')


def example02():
    logging.basicConfig(level=logging.INFO)
    log.info('create item')
    # crete item 'test' in indexSet 0
    with Byneuron() as r:
        r.create_item(name='test')


def example03():
    logging.basicConfig(level=logging.INFO)
    log.info('get event')
    # crete item 'test' in indexSet 0
    with Byneuron() as r:
        e = r.get_numberevent_key(
            key='b3875301-23ae-46ce-bf11-53f53a9bceb8',
            indexset='7710db50-7088-11ed-93aa-db27429c6866')
        log.info('found event %s: %s', e, e._datamodel)

        if e.deleted:
            e = r.delete_event(e, undo=True)
            log.info('undeleted example event %s', e)
        else:
            e = r.delete_event(e)
            log.info('deleted example event %s', e)


def example04():
    logging.basicConfig(level=logging.INFO)
    log.info('get event')
    # crete item 'test' in indexSet 0
    with Byneuron() as r:
        events = r.get_numberevent_keys(
            keys=[
                'b47dd72c-a2a3-43fe-a7c9-bda6634da6f5',
                'f036989b-9a28-4c94-8ac4-4a1234d2cf74',
                '7aa556e0-c1c1-4de0-9a04-a223c4eb7aac',
                'cc6bc7d3-048d-4ed0-a199-3b884f34236d'
            ],
            indexset=True)
        log.info('found event %s', events)
        return


if __name__ == '__main__':
    example01()
