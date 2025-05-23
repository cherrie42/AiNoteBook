// src/screens/NoteEditorScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, ScrollView, ActivityIndicator } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Audio } from 'expo-av';
import { MaterialIcons } from '@expo/vector-icons';

const NoteEditorScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { noteId } = route.params || {};
  
  const [note, setNote] = useState({ title: '', content: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recording, setRecording] = useState(null);
  
  useEffect(() => {
    if (noteId) {
      fetchNote(noteId);
    }
  }, [noteId]);
  
  const fetchNote = async (id) => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://your-api-url/notes/${id}`);
      const data = await response.json();
      setNote(data);
    } catch (error) {
      console.error('Error fetching note:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const saveNote = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://your-api-url/notes', {
        method: noteId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(note)
      });
      
      if (response.ok) {
        navigation.goBack();
      } else {
        console.error('Failed to save note');
      }
    } catch (error) {
      console.error('Error saving note:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const startRecording = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording', error);
    }
  };
  
  const stopRecording = async () => {
    setIsRecording(false);
    await recording.stopAndUnloadAsync();
    
    const uri = recording.getURI();
    // 上传录音到服务器
    uploadAudio(uri);
  };
  
  const uploadAudio = async (uri) => {
    try {
      const formData = new FormData();
      formData.append('audio', {
        uri,
        name: 'recording.mp3',
        type: 'audio/mpeg',
      });
      
      const response = await fetch('http://your-api-url/audio/transcribe', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setNote(prev => ({
          ...prev,
          content: prev.content + '\n\n' + data.transcription
        }));
      }
    } catch (error) {
      console.error('Error uploading audio:', error);
    }
  };
  
  return (
    <ScrollView style={{ padding: 16 }}>
      {isLoading ? (
        <ActivityIndicator size="large" style={{ marginTop: 20 }} />
      ) : (
        <>
          <TextInput
            style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 16 }}
            placeholder="标题"
            value={note.title}
            onChangeText={text => setNote(prev => ({ ...prev, title: text }))}
          />
          
          <TextInput
            style={{ fontSize: 16, minHeight: 300 }}
            placeholder="开始输入笔记内容..."
            multiline
            value={note.content}
            onChangeText={text => setNote(prev => ({ ...prev, content: text }))}
          />
          
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 20 }}>
            <Button title="保存" onPress={saveNote} />
            
            {isRecording ? (
              <Button 
                title="停止录音" 
                onPress={stopRecording} 
                color="red" 
              />
            ) : (
              <Button 
                title="录音" 
                onPress={startRecording} 
                color="green" 
              />
            )}
          </View>
          
          {note.summary && (
            <View style={{ marginTop: 20, padding: 10, backgroundColor: '#f0f0f0', borderRadius: 8 }}>
              <Text style={{ fontWeight: 'bold' }}>AI摘要:</Text>
              <Text>{note.summary}</Text>
            </View>
          )}
          
          {note.keywords.length > 0 && (
            <View style={{ marginTop: 10 }}>
              <Text style={{ fontWeight: 'bold' }}>关键词:</Text>
              <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
                {note.keywords.map(keyword => (
                  <Text 
                    key={keyword} 
                    style={{ 
                      backgroundColor: '#e0e0e0', 
                      padding: 5, 
                      borderRadius: 4, 
                      margin: 2 
                    }}
                  >
                    {keyword}
                  </Text>
                ))}
              </View>
            </View>
          )}
        </>
      )}
    </ScrollView>
  );
};

export default NoteEditorScreen;

// src/screens/KnowledgeGraphScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';
import { useRoute } from '@react-navigation/native';

const KnowledgeGraphScreen = () => {
  const route = useRoute();
  const { knowledgeGraph } = route.params;
  const [isLoading, setIsLoading] = useState(true);
  
  // 将知识图谱数据转换为JSON格式
  const graphJson = JSON.stringify(knowledgeGraph);
  
  // 创建知识图谱可视化的HTML
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>知识图谱</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
      <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.8/dist/chart.umd.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/mindmap.js@1.0.0/dist/mindmap.min.js"></script>
    </head>
    <body class="bg-gray-100 p-4">
      <div id="mindmap" class="w-full h-[500px] bg-white rounded-lg shadow-lg"></div>
      
      <script>
        const data = ${graphJson};
        
        // 使用mindmap.js绘制知识图谱
        const mindmap = new Mindmap(document.getElementById('mindmap'), {
          data: data,
          node: {
            colors: ['#4285F4', '#EA4335', '#FBBC05', '#34A853'],
            font: {
              size: 14,
              color: '#333'
            }
          },
          line: {
            color: '#999',
            width: 2
          },
          direction: 'right',
          spacingX: 80,
          spacingY: 40
        });
        
        // 通知React Native页面已加载完成
        setTimeout(() => {
          window.ReactNativeWebView.postMessage('loaded');
        }, 1000);
      </script>
    </body>
    </html>
  `;
  
  const onMessage = (event) => {
    if (event.nativeEvent.data === 'loaded') {
      setIsLoading(false);
    }
  };
  
  return (
    <View style={styles.container}>
      {isLoading ? (
        <ActivityIndicator size="large" style={styles.loadingIndicator} />
      ) : null}
      <WebView
        source={{ html: htmlContent }}
        onMessage={onMessage}
        style={styles.webView}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingIndicator: {
    marginTop: 20,
  },
  webView: {
    flex: 1,
  },
});

export default KnowledgeGraphScreen;

// src/screens/ReviewPlanScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { FontAwesome } from '@expo/vector-icons';
import { format, isToday, isTomorrow } from 'date-fns';

const ReviewPlanScreen = () => {
  const route = useRoute();
  const { reviewPlan } = route.params;
  const [sortedPlan, setSortedPlan] = useState([]);
  
  useEffect(() => {
    if (reviewPlan && reviewPlan.length > 0) {
      // 按复习日期排序
      const sorted = [...reviewPlan].sort((a, b) => {
        return new Date(a.date) - new Date(b.date);
      });
      setSortedPlan(sorted);
    }
  }, [reviewPlan]);
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    if (isToday(date)) {
      return '今天';
    } else if (isTomorrow(date)) {
      return '明天';
    }
    return format(date, 'MM月dd日');
  };
  
  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.reviewItem}>
      <View style={styles.dateContainer}>
        <FontAwesome name="calendar" size={20} color="#4285F4" />
        <Text style={styles.dateText}>{formatDate(item.date)}</Text>
      </View>
      
      <View style={styles.contentContainer}>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.description}>{item.description}</Text>
      </View>
      
      <View style={styles.statusContainer}>
        <FontAwesome name="angle-right" size={20} color="#999" />
      </View>
    </TouchableOpacity>
  );
  
  return (
    <View style={styles.container}>
      {sortedPlan.length > 0 ? (
        <FlatList
          data={sortedPlan}
          renderItem={renderItem}
          keyExtractor={(item, index) => index.toString()}
          contentContainerStyle={styles.listContainer}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <FontAwesome name="book" size={40} color="#ccc" />
          <Text style={styles.emptyText}>暂无复习计划</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  listContainer: {
    padding: 16,
  },
  reviewItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  dateContainer: {
    width: 60,
    alignItems: 'center',
  },
  dateText: {
    marginTop: 4,
    fontSize: 12,
    color: '#666',
  },
  contentContainer: {
    flex: 1,
    marginLeft: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  statusContainer: {
    width: 30,
    alignItems: 'flex-end',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
    color: '#999',
  },
});

export default ReviewPlanScreen;