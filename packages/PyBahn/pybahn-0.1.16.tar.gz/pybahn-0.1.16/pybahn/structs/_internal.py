from dataclasses import dataclass
from typing import Optional
from . import Products
from datetime import datetime, timedelta, timezone

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

import json, requests, json, typing


class Serializable:
    def __repr__(self):
        return json.dumps(self, default=self._default, indent=4, ensure_ascii=False)

    @staticmethod
    def _default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, (list, tuple, set)):
            return [Serializable._default(i) for i in o]
        elif isinstance(o, dict):
            return {k: Serializable._default(v) for k, v in o.items()}
        elif hasattr(o, "__dict__"):
            return {k: Serializable._default(v) for k, v in o.__dict__.items()}
        else:
            return str(o)

    
@dataclass
class Location(Serializable):
    latitude: str
    longitude: str

@dataclass
class BaseNamedStop(Serializable):
    evaNumber: Optional[str] = None
    name: Optional[str] = None
    canceled: Optional[bool] = None
    additional: Optional[bool] = None
    separation: Optional[bool] = None
    slug: Optional[str] = None
    displayPriority: Optional[int] = None
    nameParts: Optional[list] = None

    def __post_init__(self):
        self.id = self.evaNumber


class StopPlace(BaseNamedStop): pass

class Destination(BaseNamedStop): pass

class Stop(BaseNamedStop): pass

class Message(Serializable):
    def __init__(self, text = "", type = "", change = "", important: bool = False, **kwargs):
        self.text: str = text
        self.type: str = type
        self.change: bool = change
        self.important: bool = important


class DepArrBase(Serializable):
    def __init__(self, bahnhofsId = "", zeit = "", ezZeit="", gleis = "", ezGleis = "", ueber = [], journeyId = "", verkehrmittel = {'mittelText': ""}, terminus = "", meldungen = [], station_name = "", **kwargs):
        self.station_id = bahnhofsId
        self.time: datetime = datetime.fromisoformat(zeit)
        self.time_delayed: datetime = datetime.fromisoformat(ezZeit) if ezZeit else None
        self.planed_platform = gleis
        self.platform = ezGleis
        self.via: typing.List[str] = ueber
        self.journey_id: str = journeyId
        self.line_name: str = verkehrmittel['mittelText']
        self.end_station: str = terminus
        self.station_name: str = station_name

    def export(self):
        styles = getSampleStyleSheet()
        story = []
        class_ = self.__class__.__name__

        filename = f"{class_}_{self.station_name}.pdf"
        story.append(Paragraph(f"{class_}s board", styles["Title"]))
        data = [["Time", "Delayed", "Line", "To", "Platform"]]

        story.append(Paragraph(self.station_name, styles['Heading2']))
        story.append(Spacer(1, 12))
        from .._core import PyBahn
        departures: list[DepArrBase] = getattr(PyBahn(), f"{class_.lower()}s")(self.station_name)

        doc = SimpleDocTemplate(filename, pagesize=A4)

        # Title
        story.append(Spacer(1, 0.2 * inch))

        # Fill table rows
        for dep in departures:
            time_str = dep.time.strftime("%H:%M")
            delayed_str = dep.time_delayed.strftime("%H:%M") if dep.time_delayed else "-"
            platform_str = dep.platform if dep.platform else dep.planed_platform

            data.append([
                time_str,
                delayed_str,
                dep.line_name,
                dep.end_station,
                platform_str
            ])

        # Create the table
        table = Table(data, repeatRows=1)

        # Style the table
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))

        story.append(table)
        doc.build(story)
        return filename

class Departure(DepArrBase): ...

class Arrival(DepArrBase): ...



class Station(Serializable):
    def __init__(self, name: str, id: str, lid: str, lat: int = 0, lon: str = 0, products: list = [], stopover_time: int = 0, **kwargs):
        self.name: str = name
        self.id: str = id
        self.lid: str = lid
        self.stopover_time: int = stopover_time
        self.location: Location = Location(lat, lon)
        self.products: typing.List[Products] = products

class Operator(Serializable):
    def __init__(self, code, hatShop, kuerzel, description, logo, shortDescription, **kwargs):
        self.id: int = int(code)
        self.has_shop: bool = hatShop
        self.code: str = kuerzel
        self.description: str = description
        self.logo: str = logo
        self.short_description: str = shortDescription

class J_StopOver(Serializable):
    def __init__(self, id, abfahrtsZeitpunkt = None, ezAbfahrtsZeitpunkt = None, ankunftsZeitpunkt = None, ezAnkunftsZeitpunkt = None, auslastungsmeldungen = None, gleis = None, ezGleis = None, haltTyp = None, name = None, risNotizen = None, bahnhofsInfoId = None, extId = None, himMeldungen = None, **kwargs):
        self.id = id
        self.departure_time: str = abfahrtsZeitpunkt
        self.arrival_time: str = ankunftsZeitpunkt
        #self.auslastungsmeldungen = auslastungsmeldungen # Кол. Людей
        self.platform: str = gleis
        #self.haltTyp: str = haltTyp
        self.station_name: str = name
        #self.risNotizen: list = risNotizen
        #self.bahnhofsInfoId: str = bahnhofsInfoId
        self.station_id: str = extId
        #self.himMeldungen = himMeldungen
        #self.routeIdx = routeIdx
        #self.priorisierteMeldungen = priorisierteMeldungen

class info_of_mean_of_transport(Serializable):
    def __init__(self, dict: dict):
        self.category: str = dict['kategorie']
        self.key: str = dict['key']
        self.value: str = dict['value']
        self.sections_note: typing.Optional[str] = dict.get("teilstreckenHinweis", None)

class J_means_of_transport(Serializable):
    def __init__(self, name = None, nummer = None, richtung = None, zugattribute = None, kurzText = None, mittelText = None, langText = None, **kwargs):
        self.name: str = name
        self.transport_way_id: str = nummer
        self.direction: str = richtung
        self.info: typing.List[info_of_mean_of_transport] = [info_of_mean_of_transport(d) for d in zugattribute]
        self.short_name: str = kurzText
        self.middle_name: str = mittelText
        self.full_name: str = langText

class Connection(Serializable):
    """
    Represents a leg of a journey, containing details such as departure and arrival times and stations,
    the means of transport used, and a list of intermediate stopovers.

    Attributes:
        departure_time (str): Scheduled departure time.
        arrival_time (str): Scheduled arrival time.
        departure_station (str): Name of the departure station.
        arrival_station (str): Name of the arrival station.
        stopovers (List[J_StopOver]): Intermediate stops during the connection.
        journeyId (str): Identifier for the journey leg.
        means_of_transport (J_means_of_transport): Transport method used for the connection.
    """
    def __init__(self, risNotizen = None, himMeldungen = None, priorisierteMeldungen = None, externeBahnhofsinfoIdOrigin = None, externeBahnhofsinfoIdDestination = None, abfahrtsZeitpunkt = None, ezAbfahrtsZeitpunkt = None, abfahrtsOrt = None, abfahrtsOrtExtId = None, abschnittsDauer = None, ezAbschnittsDauerInSeconds = None, abschnittsAnteil = None, ankunftsZeitpunkt = None, ezAnkunftsZeitpunkt = None, ankunftsOrt = None, ankunftsOrtExtId = None, auslastungsmeldungen = None, halte = None, idx = None, journeyId = None, verkehrsmittel = None, iceSprinterNote = None, **kwargs):
        #self.risNotizen = risNotizen
        #self.himMeldungen = himMeldungen
        #self.priorisierteMeldungen = priorisierteMeldungen
        #self.externeBahnhofsinfoIdOrigin = externeBahnhofsinfoIdOrigin
        #self.externeBahnhofsinfoIdDestination = externeBahnhofsinfoIdDestination
        self.departure_time: str = abfahrtsZeitpunkt
        self.departure_station: str = abfahrtsOrt
        self.departure_delay: str = ezAbfahrtsZeitpunkt
        #self.iceSprinterNote = iceSprinterNote
        #self.abfahrtsOrtExtId = abfahrtsOrtExtId
        #self.abschnittsDauer = abschnittsDauer
        #self.abschnittsAnteil = abschnittsAnteil
        #self.ezAbschnittsDauerInSeconds = ezAbschnittsDauerInSeconds
        self.arrival_time: str = ankunftsZeitpunkt
        self.arrival_station: str = ankunftsOrt
        #self.ankunftsOrtExtId = ankunftsOrtExtId
        #self.auslastungsmeldungen = auslastungsmeldungen
        self.stopovers: typing.List[J_StopOver] = [J_StopOver(**stop) for stop in halte] if halte else []
        #self.idx = idx
        self.journeyId: str = journeyId
        self.means_of_transport: J_means_of_transport = J_means_of_transport(**verkehrsmittel)

class occupancy_level(Serializable):
    def __init__(self, dict: dict):
        self._class: str = dict['klasse']
        self.level: int = int(dict['stufe'])
        self.as_short_text: str = dict['kurzText']
        self.as_full_text: str = dict['langText'] if 'langText' in dict else None

class Journey(Serializable):
    """
    Represents a full journey from a departure station to a destination, including all connections.

    Attributes:
        trip_lid (str): Context-based ID for this journey.
        changes_amont (int): Number of transfers during the journey.
        departure_name (str): Name of the departure station.
        arrival_name (str): Name of the destination station.
        connections (List[Connection]): List of connections (legs) within the journey.
        journey_time_in_seconds (int): Estimated journey duration in seconds.
        is_alternative_connection (bool): Whether this is an alternative route.
        preis (str): Ticket price, if available.
    """
    def __init__(self, tripId = None, ctxRecon = None, verbindungsAbschnitte = None, umstiegsAnzahl = None, verbindungsDauerInSeconds = None, ezVerbindungsDauerInSeconds = None, isAlternativeVerbindung = None, auslastungsmeldungen = None, auslastungstexte = None, himMeldungen = None, risNotizen = None, priorisierteMeldungen = None, reservierungsMeldungen = None, isAngebotseinholungNachgelagert = None, isAlterseingabeErforderlich = None, serviceDays = None, angebotsPreis = None, angebotsPreisKlasse = None, hasTeilpreis = None, reiseAngebote = None, hinRueckPauschalpreis = None, isReservierungAusserhalbVorverkaufszeitraum = None, gesamtAngebotsbeziehungList = None, ereignisZusammenfassung = None, meldungen = None, meldungenAsObject = None, angebotsInformationen = None, angebotsInformationenAsObject = None, abPreisInfo: dict = None, **kwargs):
        #self.tripId: str = tripId
        self.trip_lid: str = ctxRecon
        self.changes_amont: int = umstiegsAnzahl
        self.departure_name: str = verbindungsAbschnitte[0]['abfahrtsOrt']
        self.arrival_name: str = verbindungsAbschnitte[-1]['ankunftsOrt']
        self.connections: typing.List[Connection] = [Connection(**stop) for stop in verbindungsAbschnitte] if verbindungsAbschnitte else []
        self.departure_time: str = self.connections[0].departure_time
        self.arrival_time: str = self.connections[-1].arrival_time
        self.journey_time_in_seconds: int = verbindungsDauerInSeconds
        #self.journey_time_in_seconds_e: int = ezVerbindungsDauerInSeconds
        self.is_alternative_connection: bool = isAlternativeVerbindung
        #self.auslastungsmeldungen = auslastungsmeldungen
        self.occupancy_level: typing.List[occupancy_level] = [occupancy_level(d) for d in auslastungstexte]
        #self.himMeldungen = himMeldungen
        #self.risNotizen = risNotizen
        #self.priorisierteMeldungen = priorisierteMeldungen
        #self.reservierungsMeldungen = reservierungsMeldungen
        self.additional_messages: typing.List[str] = meldungen
        #self.meldungenAsObject = meldungenAsObject
        #self.isAngebotseinholungNachgelagert: bool = isAngebotseinholungNachgelagert
        #self.isAlterseingabeErforderlich: bool = isAlterseingabeErforderlich
        #self.serviceDays = serviceDays
        self.price = str(angebotsPreis['betrag']) + " " + angebotsPreis['waehrung'] if angebotsPreis else None
        self.price_without_sale = (
            f"{sp['betrag']}{sp['waehrung']}"
            if (sp := abPreisInfo.get("streichpreis", None) if isinstance(abPreisInfo, dict) else {}) and 
            isinstance(sp, dict) and 
            "betrag" in sp and 
            "waehrung" in sp
            else None
        )
        #self.angebotsPreisKlasse: str = angebotsPreisKlasse
        #self.hasTeilpreis: bool = hasTeilpreis
        #self.reiseAngebote = reiseAngebote
        #self.angebotsInformationen = angebotsInformationen
        #self.angebotsInformationenAsObject = angebotsInformationenAsObject
        #self.hinRueckPauschalpreis: bool = hinRueckPauschalpreis
        #self.isReservierungAusserhalbVorverkaufszeitraum: bool = isReservierungAusserhalbVorverkaufszeitraum
        #self.gesamtAngebotsbeziehungList = gesamtAngebotsbeziehungList
    
    def get_db_link(self):
        """Returns a link compatible with `DB Navigator` and [int.bahn.de](https://int.bahn.de) """
        url = "https://int.bahn.de/web/api/angebote/verbindung/teilen"
        name_1 = self.departure_name
        name_2 = self.arrival_name
        if self.connections[0].departure_time:
            ti = self.connections[0].departure_time
            dt = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
            time_ = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            time_ = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

        ctx = self.trip_lid

        r = requests.post(url, json={
            "startOrt": name_1,
            "zielOrt": name_2,
            "hinfahrtDatum": time_,
            "hinfahrtRecon": ctx
        }, headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Accept": "application/json"
        })

        if r.json()['vbid']:
            link = "https://int.bahn.de/en/buchung/start?vbid=" + r.json()['vbid']

            return link
        
        else:
            raise ValueError(r.text)
    
    def export(self):        
        filename = f"journey_{self.departure_name}_{self.arrival_name}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(f"<b>{self.departure_name} → {self.arrival_name}</b>", styles["Title"]))

            # Journey info
        duration = str(timedelta(seconds=self.journey_time_in_seconds))
        info = (
            f"<b>Departure:</b> {datetime.fromisoformat(self.departure_time).strftime("%a %d. %b, %H:%M")}<br/>"
            f"<b>Arrival:</b> {datetime.fromisoformat(self.arrival_time).strftime("%a %d. %b, %H:%M")}<br/>"
            f"<b>Duration:</b> {duration}<br/>"
            f"<b>Changes:</b> {self.changes_amont or 0}<br/>"
            f"<b>Price:</b> {self.preis or 'N/A'}"
        )
        story.append(Paragraph(info, styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Each connection in free style
        for idx, conn in enumerate(self.connections, start=1):
            story.append(Paragraph(f"<b>{conn.departure_station}</b>", styles["Heading3"]))
            story.append(Spacer(1, 0.2 * inch))

            dep_time = conn.departure_time
            arr_time = conn.arrival_time
            try:
                dep_time = datetime.fromisoformat(dep_time).strftime("%H:%M")
            except:
                dep_time = "null"
            try:
                arr_time = datetime.fromisoformat(arr_time).strftime("%H:%M")
            except:
                arr_time = "null"

            line_name = getattr(conn.means_of_transport, "full_name", "Unknown")
            platform = getattr(conn.stopovers[0], "platform", "-") if conn.stopovers else "-"

            details = (
                f"      <b>Line:</b> {line_name}<br/>"
                f"      <b>Departure:</b> {dep_time}<br/>"
                f"      <b>Platform:</b> {platform}<br/>"
                f"      <b>Direction:</b> {conn.means_of_transport.direction}<br/>"
                f"      <b>Arrival:</b> {arr_time}<br/>"
            )
            story.append(Paragraph(details, styles["Normal"]))
            if idx == len(self.connections):
                story.append(Paragraph(f"<b>{conn.arrival_station}</b>", styles["Heading3"]))
            story.append(Spacer(1, 0.2 * inch))

        doc.build(story)
        return filename

class Coordinate(Serializable):
    def __init__(self, lng, lat):
        self.lng: float = lng
        self.lat: float = lat

class Polyline(Serializable):
    def __init__(self, coordinates: dict, delta: bool):
        self.coordinates = [Coordinate(**c) for c in coordinates]
        self.delta = delta

if __name__ == "__main__":
    raise RuntimeError("This module is not intended to be run or imported directly.")