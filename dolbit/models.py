import datetime

def get_date(timestamp):
    time = datetime.datetime.fromtimestamp(timestamp,
                                           tz=datetime.timezone.utc)
    return time.date()


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
        self.start = get_date(int(data['date_start']))
        self.end = get_date(int(data['date_end']))
        self.quantity = int(data['qty'])

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
        self.date = get_date(int(data['date_contrat']))
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
            if line.status == ContractLine.STATUS_RUNNING and line.end < now:
                self._is_expired = True
                break
        return self._is_expired

    def __str__(self):
        result = f'{self.pk}: {self.ref} ({self.date}):'
        for line in self.lines:
            result = f'{result}\n\t{line}'
        return result

    def __repr__(self):
        return self.__str__()
