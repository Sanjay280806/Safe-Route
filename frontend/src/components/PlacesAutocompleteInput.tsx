import { useMapsLibrary } from "@vis.gl/react-google-maps";
import { useEffect, useRef } from "react";
import { bboxToBoundsLiteral, type Bbox } from "../config/googleMaps";
import type { LatLng } from "../types";
import { useGoogleMapsConfigured } from "./GoogleMapsProvider";

export interface PlaceSelection {
  location: LatLng;
  label: string;
}

interface PlacesAutocompleteInputProps {
  id: string;
  placeholder: string;
  value: string;
  bounds: Bbox;
  disabled?: boolean;
  onChange: (value: string) => void;
  onPlaceSelect: (place: PlaceSelection) => void;
  onError?: (message: string) => void;
}

export function PlacesAutocompleteInput({
  id,
  placeholder,
  value,
  bounds,
  disabled = false,
  onChange,
  onPlaceSelect,
  onError,
}: PlacesAutocompleteInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const placesLibrary = useMapsLibrary("places");
  const configured = useGoogleMapsConfigured();

  useEffect(() => {
    if (!placesLibrary || !inputRef.current || disabled) return;

    const autocomplete = new placesLibrary.Autocomplete(inputRef.current, {
      bounds: bboxToBoundsLiteral(bounds),
      strictBounds: false,
      componentRestrictions: { country: "in" },
      fields: ["geometry", "name", "formatted_address"],
    });

    const listener = autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();
      const location = place.geometry?.location;

      if (!location) {
        onError?.("Could not resolve that place. Try another search or click the map.");
        return;
      }

      const label = place.name || place.formatted_address || "Selected place";
      onPlaceSelect({
        location: { lat: location.lat(), lon: location.lng() },
        label,
      });
      onChange(label);
    });

    return () => {
      listener.remove();
      google.maps.event.clearInstanceListeners(autocomplete);
    };
  }, [bounds, disabled, onChange, onError, onPlaceSelect, placesLibrary]);

  return (
    <input
      id={id}
      ref={inputRef}
      className="places-autocomplete-input"
      type="text"
      value={value}
      placeholder={placeholder}
      disabled={disabled || !configured}
      autoComplete="off"
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
