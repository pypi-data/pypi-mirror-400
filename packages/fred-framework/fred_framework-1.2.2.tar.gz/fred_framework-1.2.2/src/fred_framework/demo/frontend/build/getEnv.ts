import path from "path";

export function isDevFn(mode: string): boolean {
  return mode === "development";
}

export function isProdFn(mode: string): boolean {
  return mode === "production";
}

export function isTestFn(mode: string): boolean {
  return mode === "test";
}

/**
 * Whether to generate package preview
 */
export function isReportMode(): boolean {
  return process.env.VITE_REPORT === "true";
}

// Read all environment variable configuration files to process.env
export function wrapperEnv(envConf: Recordable): ViteEnv {
  const ret: any = {};

  // First pass: collect all environment variables
  for (const envName of Object.keys(envConf)) {
    let realName = envConf[envName].replace(/\\n/g, "\n");
    realName = realName === "true" ? true : realName === "false" ? false : realName;
    if (envName === "VITE_PORT") realName = Number(realName);
    ret[envName] = realName;
  }

  // Second pass: replace variables in VITE_PROXY
  if (ret.VITE_PROXY) {
    try {
      let proxyStr = String(ret.VITE_PROXY);
      // Replace variables in format: ${VAR_NAME}
      // Process in reverse order to avoid replacing parts of already replaced values
      const sortedVarNames = Object.keys(ret).sort((a, b) => b.length - a.length);
      for (const varName of sortedVarNames) {
        const varValue = String(ret[varName]);
        // Escape special characters in variable value for JSON
        const escapedValue = varValue.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
        // Replace ${VAR_NAME} format in JSON string
        proxyStr = proxyStr.replace(new RegExp(`\\$\\{${varName}\\}`, 'g'), escapedValue);
      }
      ret.VITE_PROXY = JSON.parse(proxyStr);
    } catch (error) {
      console.warn('Failed to parse VITE_PROXY:', error);
    }
  }

  return ret;
}

/**
 * Get user root directory
 * @param dir file path
 */
export function getRootPath(...dir: string[]) {
  return path.resolve(process.cwd(), ...dir);
}
