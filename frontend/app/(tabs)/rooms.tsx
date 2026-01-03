// App.tsx
import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import {
  FlatList,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';

const rooms = [
  {
    id: 1,
    tag: '倫理',
    members: 12,
    title: '「自由って何？」',
    updated_at: '3分前',
  },
  {
    id: 2,
    tag: '幸福',
    members: 8,
    title: '「幸せとは状態か過程か？」',
    updated_at: '1時間前',
  },
  {
    id: 3,
    tag: '政治哲学',
    members: 20,
    title: '「民主主義は最善か？」',
    updated_at: '昨日',
  },
  {
    id: 4,
    tag: '政治哲学',
    members: 20,
    title: '「民主主義は最善か？」',
    updated_at: '昨日',
  },
];

type RoomCardProps={
  id:number,
  tag:string,
  members:number,
  title:string,
  updated_at:string
}

function RoomCard({id,tag,members,title,updated_at}:RoomCardProps){
  return (
    <View style={styles.card} key={id}>
      <View style={styles.tagContainer}>
        <Text style={styles.tagText}>
          #{tag} {members}人
        </Text>
      </View>
      <Text style={styles.cardTitle}>{title}</Text>
      <Text style={styles.cardSub}>最終更新: {updated_at}</Text>
    </View>
  )
}

export default function App() {
  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="dark-content" />
      {/* header */}
      <View style={styles.header}>
        <Ionicons name="menu" size={28} color="#1f2933" />
        <Text style={styles.headerTitle}>ルーム</Text>
        <View style={{ width: 28 }} />
      </View>

      {/* content */}
      <FlatList
        data={rooms}
        keyExtractor={(item) => `${item.id}`}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <RoomCard id={item.id} tag={item.tag} members={item.members} title={item.title} updated_at={item.updated_at}/>
        )}
      />

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#f5f7fb',
  },
  header: {
    height: 56,
    paddingHorizontal: 16,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#e5e7eb',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1f2933',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingVertical: 16,
    paddingBottom: 96,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 16,
    marginBottom: 16,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: '#e5e7eb',
  },
  tagContainer: {
    alignSelf: 'flex-start',
    backgroundColor: '#0066cc',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 6,
    marginBottom: 8,
  },
  tagText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 14,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 8,
  },
  cardSub: {
    fontSize: 14,
    color: '#6b7280',
  },
  tabBar: {
    height: 72,
    flexDirection: 'row',
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#e5e7eb',
    backgroundColor: '#ffffff',
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabLabel: {
    fontSize: 14,
    marginTop: 4,
    color: '#9ca3af',
  },
  tabLabelActive: {
    color: '#0070c9',
    fontWeight: '700',
  },
});
