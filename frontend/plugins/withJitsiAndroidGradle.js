const { withProjectBuildGradle, withAndroidManifest } = require('expo/config-plugins');

// @jitsi/react-native-sdk の Android向けnode_modules/@jitsi/react-native-sdk/android/build.gradle が、
// rootProject.ext.gradlePluginVersion を無条件に参照する（存在しないとビルド自体が失敗する）。
// 現行のExpoテンプレートのandroid/build.gradleはこのextを定義しないため、
// `expo prebuild` の度に自動で追記されるよう config plugin 化した。
// バージョンはnode_modules/@react-native/gradle-plugin/gradle/libs.versions.tomlのagpと合わせている。
// 参考: node_modules/@jitsi/react-native-sdk/README.md の「Android」セクション
const GRADLE_PLUGIN_VERSION = '8.11.0';

const REQUIRED_PERMISSIONS = [
  'android.permission.RECORD_AUDIO',
  'android.permission.CAMERA',
  'android.permission.FOREGROUND_SERVICE',
  'android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION',
];

function withJitsiProjectBuildGradle(config) {
  return withProjectBuildGradle(config, (config) => {
    if (config.modResults.language !== 'groovy') {
      throw new Error('withJitsiAndroidGradle only supports Groovy android/build.gradle files');
    }

    let contents = config.modResults.contents;

    if (!contents.includes('gradlePluginVersion')) {
      contents = contents.replace(
        'buildscript {',
        `buildscript {\n  ext {\n    gradlePluginVersion = "${GRADLE_PLUGIN_VERSION}"\n  }`
      );
    }

    config.modResults.contents = contents;
    return config;
  });
}

function withJitsiAndroidManifest(config) {
  return withAndroidManifest(config, (config) => {
    const manifest = config.modResults.manifest;
    manifest['uses-permission'] = manifest['uses-permission'] || [];

    for (const permission of REQUIRED_PERMISSIONS) {
      const exists = manifest['uses-permission'].some(
        (item) => item.$ && item.$['android:name'] === permission
      );
      if (!exists) {
        manifest['uses-permission'].push({ $: { 'android:name': permission } });
      }
    }

    return config;
  });
}

module.exports = function withJitsiAndroidGradle(config) {
  config = withJitsiProjectBuildGradle(config);
  config = withJitsiAndroidManifest(config);
  return config;
};
