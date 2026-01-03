import { ThemedText } from '@/components/themed-text';
import Ionicons from '@expo/vector-icons/Ionicons';
import { Image } from 'expo-image';
import { Button, StyleSheet, View } from 'react-native';

import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedView } from '@/components/themed-view';

export default function HomeScreen() {
  
  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#A1CEDC', dark: '#1D3D47' }}
      headerImage={
        <Image
          source={require('@/assets/images/partial-react-logo.png')}
          style={styles.reactLogo}
        />
      }>
      <ThemedText type="subtitle" style={styles.textContainer}>Today Question</ThemedText>
      <ThemedView style={styles.buttonWrapper}>
      <ThemedText type="subtitle" style={styles.textContainer}>What is moral?</ThemedText>
      </ThemedView>
      <View style={styles.blankContainer}>
      </View>
      <View style={styles.buttonWrapper}>
      <Ionicons name="call" size={36} color="black" />
      <Button title="Matching Start"
      color="red"
      accessibilityLabel="Learn more about this purple button"
      />
      </View>
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  textContainer:{
    textAlign:"center"
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stepContainer: {
    gap: 8,
    marginBottom: 8,
  },
  reactLogo: {
    height: 178,
    width: 290,
    bottom: 0,
    left: 0,
    position: 'absolute',
  },
  buttonWrapper: {
    borderWidth: 2,
    borderColor: "#007AFF",
    borderRadius: 8,
    overflow: "hidden", // 角丸に沿わせたい場合
    padding:32,
    flexDirection: 'row',        // 横並び
    gap: 8,                      // RN 0.71+ ならアイコンとボタンの間隔に gap も使える
  },
  blankContainer:{
    height:150
  },
});
