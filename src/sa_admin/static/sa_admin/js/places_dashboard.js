import * as csv from 'https://cdn.jsdelivr.net/npm/csv-stringify@6.5.0/sync/+esm';
import { Component } from "./component.js";
import { PlacesTable } from "./places_table.js";
import { PlacesMap } from "./places_map.js";


class PlacesDashboard extends Component {
  constructor(el, places, fields) {
    super(el);

    this.places = places;
    this.fields = fields;
    this.filteredCount = this.el.querySelector('.filtered-count');
    this.totalCount = this.el.querySelector('.total-count');
    this.downloadButton = this.el.querySelector('button.download');
    this.table = new PlacesTable(this.el.querySelector('#places-table'), this.places, fields);
    this.map = new PlacesMap(this.el.querySelector('#places-map'), this.places);
  }

  fill() {
    this.table.fill();
    this.map.fill();
    this.initPlaceCounts();
    return this;
  }

  empty() {
    this.table.empty();
    this.map.empty();
    return this;
  }

  bind() {
    this.table.bind();
    this.map.bind();

    this.listeners.add('place:mouseover', this.map.dispatcher, (e) => {
      const placeId = e.detail.placeId;
      this.highlightPlace(placeId, true, false);
    });

    this.listeners.add('place:mouseout', this.map.dispatcher, (e) => {
      const placeId = e.detail.placeId;
      this.unhighlightPlace(placeId, true, false);
    });

    this.listeners.add('place:click', this.map.dispatcher, (e) => {
      const placeId = e.detail.placeId;
      this.openPlaceDetail(placeId);
    })

    this.listeners.add('place:mouseover', this.table.dispatcher, (e) => {
      const placeId = e.detail.placeId;
      this.highlightPlace(placeId, false, true);
    });

    this.listeners.add('place:mouseout', this.table.dispatcher, (e) => {
      const placeId = e.detail.placeId;
      this.unhighlightPlace(placeId, false, true);
    });

    this.listeners.add('place:click', this.table.dispatcher, (e) => {
      const placeId = e.detail.placeId;
      this.openPlaceDetail(placeId);
    });

    this.listeners.add('filter', this.table.dispatcher, (e) => {
      const predicates = this.table.head.cells
        .filter((cell) => cell.filter)
        .map((cell) => cell.filter.filterPredicate.bind(cell.filter));
      this.filterPlaces(predicates);
    });

    this.listeners.add('click', this.downloadButton, (e) => {
      e.preventDefault();
      this.downloadPlaces();
    });

    return Component.prototype.bind.call(this);
  }

  initPlaceCounts() {
    this.filteredCount.innerHTML = this.places.models.length;
    this.totalCount.innerHTML = this.places.models.length;
  }

  filterPlaces(predicates) {
    this.table.filterRows(predicates);
    this.map.filterMarkers(predicates);

    const filteredPlaces = this.places.models.filter((place) => predicates.every((predicate) => predicate(place)));
    this.filteredCount.innerHTML = filteredPlaces.length;
    this.totalCount.innerHTML = this.places.models.length;
  }

  downloadPlaces() {
    const header = [...this.fields.map((field) => field.label), 'longitude', 'latitude'];
    const data = this.places.models.map((place) => {
      const row = [];
      for (const field of this.fields) {
        row.push(place.get(field.attr));
      }
      row.push(...place.get('geometry').coordinates);
      return row;
    });

    const output = csv.stringify([header, ...data]);

    const blob = new Blob([output], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data-${(new Date()).toISOString().replace(/:/g, '').replace(/-/g, '').slice(0, 15)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  unbind() {
    this.table.unbind();
    this.map.unbind();
    return Component.prototype.unbind.call(this);
  }

  highlightPlace(placeId, skipMap = false, skipTable = false) {
    if (!skipMap) this.map.highlightMarker(placeId);
    if (!skipTable) this.table.highlightRow(placeId);
    return this;
  }

  unhighlightPlace(placeId, skipMap = false, skipTable = false) {
    if (!skipMap) this.map.unhighlightMarker(placeId);
    if (!skipTable) this.table.unhighlightRow(placeId);
    return this;
  }

  openPlaceDetail(placeId) {
    const url = `/admin/detail/${placeId}/`;
    window.open(url, '_blank').focus();
    return this;
  }
}


export { PlacesDashboard };