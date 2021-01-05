import datetime
import requests

def get_date(timestamp):
    try:
        timestamp = int(timestamp)
        time = datetime.datetime.utcfromtimestamp(timestamp)
        return time.date()
    except ValueError:
        return None

def get_timestamp(date):
    date = datetime.datetime(year=date.year, month=date.month, day=date.day)
    return (date - datetime.datetime.utcfromtimestamp(0)).total_seconds()


class ContractLine:
    STATUS_RUNNING = '4'
    STATUS_CLOSED = '5'

    def __init__(self, data):
        self.pk = int(data['id'])
        self.ref = data['ref']
        self.product = int(data['fk_product'])
        self.status = data['statut']
        self.label = data['product_label']
        self.description = data['description']
        self.start = get_date(data['date_start'])
        self.end = get_date(data['date_end'])
        self.quantity = int(data['qty'])
        self.unit_price = float(data['subprice'])

    def create(self, dol, contract):
        if self.pk != -1:
            return self
        obj = {
            'fk_product': self.product,
            'statut': self.status,
            'description': self.description,
            'date_start': get_timestamp(self.start),
            'date_end': get_timestamp(self.end),
            'qty': self.quantity,
            'subprice': self.unit_price,
        }
        self.pk = dol.post(f'/contracts/{contract}/lines', obj)
        obj = {
            'datestart': get_timestamp(self.start),
        }
        result = dol.put(f'/contracts/{contract}/lines/{self.pk}/activate', data=obj)
        return self

    def __str__(self):
        result = f'{self.quantity}x {self.ref} - {self.label}'
        result = f'{result} ({self.start} to {self.end})'
        return result

    def __repr__(self):
        return self.__str__()


class Contract:
    STATUS_DRAFT = '0'
    STATUS_VALIDATED = '1'

    def __init__(self, data):
        self.pk = data['id']
        self.ref = data['ref']
        self.status = data['statut']
        self.third_party_id = data['socid']
        self.date = get_date(int(data['date_contrat']))
        self.commercial_signature_id = data['commercial_signature_id']
        self.commercial_suivi_id = data['commercial_suivi_id']
        self.lines = [ContractLine(x) for x in data['lines']]
        self._is_closed = None
        self._is_expired = None

    def is_closed(self):
        if self._is_closed:
            return self._is_closed
        self._is_closed = True
        for line in self.lines:
            if line.status == ContractLine.STATUS_RUNNING:
                self._is_closed = False
                break
        return self._is_closed

    def is_expired(self):
        if self._is_expired:
            return self.is_expired

        if self.is_closed():
            self._is_expired = False
            return self._is_expired

        self._is_expired = False
        for line in self.lines:
            now = datetime.datetime.utcnow().date()
            if line.status == ContractLine.STATUS_RUNNING:
                if line.end and line.end < now:
                    self._is_expired = True
                    break
        return self._is_expired

    def create(self, dol):
        if self.pk != -1:
            return self
        obj = {
            'socid': self.third_party_id,
            'date_contrat': get_timestamp(self.date),
            'commercial_signature_id': self.commercial_signature_id,
            'commercial_suivi_id': self.commercial_suivi_id,
        }
        self.pk = dol.post('/contracts', obj)
        dol.post(f'/contracts/{self.pk}/validate', {'notrigger': 0})
        for line in self.lines:
            line.create(dol, self.pk)
        result = dol.get(f'/contracts/{self.pk}')
        self = Contract(result)
        return self

    def end(self, dol):
        result = dol.post(f'/contracts/{self.pk}/close', {'notrigger': '0'})
        return result

    def __str__(self):
        result = f'{self.pk}: {self.ref} ({self.date}):'
        for line in self.lines:
            result = f'{result}\n\t{line}'
        return result

    def __repr__(self):
        return self.__str__()
