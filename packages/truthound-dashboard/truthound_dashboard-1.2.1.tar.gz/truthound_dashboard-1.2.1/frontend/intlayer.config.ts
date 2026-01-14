import { Locales, type IntlayerConfig } from "intlayer";

const config: IntlayerConfig = {
  internationalization: {
    locales: [Locales.ENGLISH, Locales.KOREAN],
    defaultLocale: Locales.ENGLISH,
  },
  content: {
    contentDir: ["./src"],
    fileExtensions: [".content.ts", ".content.tsx"],
  },
};

export default config;
