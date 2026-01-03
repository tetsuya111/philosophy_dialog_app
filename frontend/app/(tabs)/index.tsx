// App.tsx
import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import {
    SafeAreaView,
    StatusBar,
    StyleSheet,
    Text,
    View,
} from 'react-native';

export default function App() {
  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="dark-content" />

      {/* header */}
      <View style={styles.header}>
        <Ionicons name="menu" size={28} color="#1f2933" />
        <Text style={styles.headerTitle}>Home</Text>
        <View style={{ width: 28 }} />
      </View>

      {/* main content */}
      <View style={styles.content}>
        {/* 今日の問い */}
        <Text style={styles.sectionTitle}>今日の問い</Text>
        <View style={styles.sectionDivider} />

        <View style={styles.questionCard}>
          <Text style={styles.questionTitle}>「自由って何？」</Text>
          <View style={styles.questionSubRow}>
            <View style={styles.questionSubLine} />
            <Text style={styles.questionSubText}>1行説明（任意）</Text>
            <View style={styles.questionSubLine} />
          </View>
        </View>
    </View>

      {/* 対話ボタン */}
      <View style={styles.callButtonWrapper}>
        <View style={styles.callButton}>
          <Ionicons name="call" size={28} color="#ffffff" />
          <Text style={styles.callButtonText}>対話をはじめる</Text>
        </View>
      </View>

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
  content: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4,
  },
  sectionDivider: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: '#e5e7eb',
    marginBottom: 16,
  },
  questionCard: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    paddingVertical: 24,
    paddingHorizontal: 16,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: '#e5e7eb',
  },
  questionTitle: {
    fontSize: 26,
    fontWeight: '800',
    color: '#111827',
    textAlign: 'center',
    marginBottom: 16,
  },
  questionSubRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  questionSubLine: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: '#d1d5db',
    flex: 1,
  },
  questionSubText: {
    marginHorizontal: 8,
    fontSize: 14,
    color: '#6b7280',
  },
  tagRow: {
    flexDirection: 'row',
    marginTop: 16,
  },
  tag: {
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 12,
  },
  tagText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 14,
  },
  callButtonWrapper: {
    paddingHorizontal: 16,
    paddingBottom: 96,
    paddingTop: 32,
  },
  callButton: {
    backgroundColor: '#111827',
    borderRadius: 999,
    paddingVertical: 18,
    paddingHorizontal: 24,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',

    // シンプルな擬似シャドウ
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    elevation: 4,
  },
  callButtonText: {
    color: '#ffffff',
    fontWeight: '800',
    fontSize: 20,
    marginLeft: 12,
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
