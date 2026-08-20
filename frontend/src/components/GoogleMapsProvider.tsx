import { APILoadingStatus, APIProvider, useApiLoadingStatus } from "@vis.gl/react-google-maps";
import { createContext, type ReactNode, useContext } from "react";
import { getGoogleMapsApiKey, GOOGLE_MAPS_LIBRARIES } from "../config/googleMaps";

interface GoogleMapsContextValue {
  configured: boolean;
}

const GoogleMapsConfigContext = createContext<GoogleMapsContextValue>({ configured: false });

export function useGoogleMapsConfigured(): boolean {
  return useContext(GoogleMapsConfigContext).configured;
}

interface GoogleMapsProviderProps {
  children: ReactNode;
}

function GoogleMapsLoadGuard({ children }: { children: ReactNode }) {
  const status = useApiLoadingStatus();

  if (status === APILoadingStatus.AUTH_FAILURE) {
    return (
      <>
        <div className="map-load-error map-load-error-inline" role="alert">
          <strong>Invalid Google Maps API key.</strong> Update <code>VITE_GOOGLE_MAPS_API_KEY</code> and enable the Maps JavaScript API.
        </div>
        {children}
      </>
    );
  }

  if (status === APILoadingStatus.FAILED) {
    return (
      <>
        <div className="map-load-error map-load-error-inline" role="alert">
          <strong>Google Maps failed to load.</strong> Check your network and Google Cloud API settings.
        </div>
        {children}
      </>
    );
  }

  return <>{children}</>;
}

export function GoogleMapsProvider({ children }: GoogleMapsProviderProps) {
  const apiKey = getGoogleMapsApiKey();

  if (!apiKey) {
    return (
      <GoogleMapsConfigContext.Provider value={{ configured: false }}>
        {children}
      </GoogleMapsConfigContext.Provider>
    );
  }

  return (
    <GoogleMapsConfigContext.Provider value={{ configured: true }}>
      <APIProvider apiKey={apiKey} libraries={[...GOOGLE_MAPS_LIBRARIES]} region="IN" language="en">
        <GoogleMapsLoadGuard>{children}</GoogleMapsLoadGuard>
      </APIProvider>
    </GoogleMapsConfigContext.Provider>
  );
}
