import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import markerIconPng from "leaflet/dist/images/marker-icon.png"
import { Icon } from 'leaflet'
import Papa from 'papaparse';
import TimePicker from 'react-time-picker';
import 'react-time-picker/dist/TimePicker.css';
import 'react-clock/dist/Clock.css';


function App() {
  const [markers, setMarkers] = useState([]);
  const [filteredMarkers, setFilteredMarkers] = useState([]);
  // coordinates for upenn
  const latitude = 39.9526;
  const longitude = -75.1652;
  const [time, setTime] = useState('10:00');


  useEffect(() => {
    const csvUrl = 'https://cors-anywhere.herokuapp.com/https://storage.googleapis.com/musa509-final-project-sk-mh/matching-pairs/matching_pairs.csv'; // Replace with the URL to your CSV file
    Papa.parse(csvUrl, {
      download: true,
      header: true,
      complete: function(results) {
        var markersData = results.data.filter(data => {
          return data.user1_id != '';
        })
        markersData = markersData.map(data => ({
          lat: parseFloat(data.avg_lat),
          lng: parseFloat(data.avg_lon),
          time: new Date(data.timestamp)
        }));
        setMarkers(markersData);
      }
    });

    onSetTime("10:00");
  }, []);

  const defaultIcon = new Icon({
    iconUrl: markerIconPng,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  });

  const onSetTime = (val) => {
    setTime(val);
    if (markers.length === 0) return;

    // all markers have same date, so set the selectedTime's date to be the same
    const refMarkerTime = markers[0].time;
    const year = refMarkerTime.getFullYear();
    const month = refMarkerTime.getMonth();
    const day = refMarkerTime.getDate();
    const selectedTime = new Date(Date.UTC(year, month, day, parseInt(val.split(':')[0]), parseInt(val.split(':')[1])));
  
    const oneHourBefore = new Date(selectedTime.getTime() - 60 * 60 * 1000);
    const oneHourAfter = new Date(selectedTime.getTime() + 60 * 60 * 1000);
    
    /// keep only markers that's within 1 hour of selected time
    const filtered = markers.filter(marker => {
      return marker.time >= oneHourBefore && marker.time <= oneHourAfter;
    });

    setFilteredMarkers(filtered);
  }

  return (
    <div>
      <h1>My Leaflet.js and React Map</h1>
      <TimePicker
      onChange={onSetTime}
      value={time}
    />
    <br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
      <MapContainer
        center={[latitude, longitude]}
        zoom={15}
        style={{ height: "90vh", width: "100vw" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {filteredMarkers.map((marker, idx) => (
          <Marker
            key={idx}
            position={[marker.lat, marker.lng]}
            icon={defaultIcon}
          />
        ))}
      </MapContainer>
    </div>
  );
}

export default App;