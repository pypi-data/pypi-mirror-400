interface IBioLibGlobals {
  getOutputFileData: (path: string) => Promise<Uint8Array>;
}

declare global {
  const biolib: IBioLibGlobals;
}

// DO NOT MODIFY: Development data files are injected at build time from gui/dev-data/ folder
const DEV_DATA_FILES: Record<string, string> = {};

const devSdkBioLib: IBioLibGlobals = {
  getOutputFileData: async (path: string): Promise<Uint8Array> => {
    console.log(`[SDK] getOutputFileData called with path: ${path}`);
    
    const normalizedPath = path.startsWith('/') ? path.slice(1) : path;
    
    if (typeof DEV_DATA_FILES !== 'undefined' && normalizedPath in DEV_DATA_FILES) {
      const base64Data = DEV_DATA_FILES[normalizedPath];
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      return bytes;
    }
    
    throw new Error(`File not found: ${path}. Add this file to the dev-data/ folder for local development.`);
  },
};

const biolib: IBioLibGlobals =
  process.env.NODE_ENV === "development"
    ? devSdkBioLib
    : (window as any).biolib;

export default biolib;
