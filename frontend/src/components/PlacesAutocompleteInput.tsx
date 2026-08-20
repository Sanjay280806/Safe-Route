import { useMapsLibrary } from "@vis.gl/react-google-maps";
import { useEffect, useRef } from "react";
import type { Bbox } from "../config/googleMaps";
import type { LatLng } from "../types";

interface PlacesAutocompleteInputProps {
  id: string;
  placeholder: string;
  value: string;
  bounds: Bbox;
  onChange: (value: string) => void;
  onPlaceSelect: (place: { location: LatLng; label: string }) => void;
  onError: (message: string) => void;
}

export function PlacesAutocompleteInput({
  id,
  placeholder,
  value,
  bounds,
  onChange,
  onPlaceSelect,
  onError,
}: PlacesAutocompleteInputProps) {
  const places = useMapsLibrary("places");
  const inputRef = useRef<HTMLInputElement | null>(null);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);

  useEffect(() => {
    if (!places || !inputRef.current) return;

    const autocomplete = new places.Autocomplete(inputRef.current, {
      bounds: new google.maps.LatLngBounds(
        { lat: bounds[0], lng: bounds[1] },
        { lat: bounds[2], lng: bounds[3] },
      ),
      componentRestrictions: { country: "in" },
      fields: ["formatted_address", "geometry", "name"],
      strictBounds: false,
    });
    autocompleteRef.current = autocomplete;

    const listener = autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();
      const location = place.geometry?.location;
      if (!location) {
        onError("Choose a location from the suggested places.");
        return;
      }

      const point = { lat: location.lat(), lon: location.lng() };
      onPlaceSelect({
        location: point,
        label: place.name ?? place.formatted_address ?? `${point.lat.toFixed(4)}, ${point.lon.toFixed(4)}`,
      });
    });

    return () => {
      listener.remove();
      autocompleteRef.current = null;
    };
  }, [bounds, onError, onPlaceSelect, places]);

  useEffect(() => {
    autocompleteRef.current?.setBounds(
      new google.maps.LatLngBounds(
        { lat: bounds[0], lng: bounds[1] },
        { lat: bounds[2], lng: bounds[3] },
      ),
    );
  }, [bounds]);

  return (
    <input
      ref={inputRef}
      id={id}
      className="places-autocomplete-input"
      type="text"
      autoComplete="off"
      placeholder={placeholder}
      value={value}
      disabled={!places}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
