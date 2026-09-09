const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// @jitsi/react-native-sdk imports its icons directly as `.svg` files (e.g.
// `import IconMic from './mic.svg'`) and expects them to be transformed into
// SVG React components via react-native-svg-transformer. Without this,
// Metro treats `.svg` as a generic asset and the import resolves to a raw
// numeric asset id, which crashes React with
// "Element type is invalid: ...but got: number" when Jitsi renders any icon.
config.transformer = {
  ...config.transformer,
  babelTransformerPath: require.resolve('react-native-svg-transformer'),
};
config.resolver = {
  ...config.resolver,
  assetExts: config.resolver.assetExts.filter((ext) => ext !== 'svg'),
  sourceExts: [...config.resolver.sourceExts, 'svg'],
};

module.exports = config;
