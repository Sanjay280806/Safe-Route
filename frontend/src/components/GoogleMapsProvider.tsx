import { APIProvider } from "@vis.gl/react-google-maps";
import { createContext, useContext, type ReactNode } from "react";
import { getGoogleMapsApiKey } from "../config/googleMaps";

const GoogleMapsConfiguredContext = createContext(false);

export function useGoogleMapsConfigured(): boolean {
  return useContext(GoogleMapsConfiguredContext);
}

export function GoogleMapsProvider({ children }: { children: ReactNode }) {
  const apiKey = getGoogleMapsApiKey();
  const configured = Boolean(apiKey);

  return (
    <GoogleMapsConfiguredContext.Provider value={configured}>
      {configured ? (
        <APIProvider apiKey={apiKey} libraries={["places"]}>
          {children}
        </APIProvider>
      ) : children}
    </GoogleMapsConfiguredContext.Provider>
  );
}
