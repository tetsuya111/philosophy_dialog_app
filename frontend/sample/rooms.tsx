import { StyleSheet, View } from 'react-native';

import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedText } from '@/components/themed-text';
import { IconSymbol } from '@/components/ui/icon-symbol';

type RoomItemProp={
    name:string
    date:string
};

function RoomItem({name,date}:RoomItemProp){
    return (
        <View style={styles.roomItemContainer}>
            <ThemedText>「{name}」</ThemedText>
            <ThemedText>{date}</ThemedText>
        </View>
    );
}

const TEST_ROOM_NAMES=[
    "What is moral?",
    "What is Imagination?"
];

export default function TabTwoScreen() {
    const test_room_elements=TEST_ROOM_NAMES.map((name,index)=>{
        return (<RoomItem key={index.toString()} name={name} date="2025/1/1 12:00:30"/>)
    });
  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#D0D0D0', dark: '#353636' }}
      headerImage={
        <IconSymbol
          size={310}
          color="#808080"
          name="chevron.left.forwardslash.chevron.right"
          style={styles.headerImage}
        />
      }>
        {test_room_elements}
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  roomItemContainer:{
    borderWidth: 2,
    borderColor: "#007AFF",
    borderRadius: 8,
    padding:24
  },
  headerImage: {
    color: '#808080',
    bottom: -90,
    left: -35,
    position: 'absolute',
  },
  titleContainer: {
    flexDirection: 'row',
    gap: 8,
  },
});
