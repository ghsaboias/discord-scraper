'use client'

import ImageModal from '@/components/ImageModal'
import VideoModal from '@/components/VideoModal'
import { Channel } from '@/types/discord'
import { useEffect, useState } from 'react'

// Helper function to extract username from URLs
const extractUsernameFromUrl = (url: string): string | null => {
  if (url.includes('t.me/')) {
    return url.split('t.me/')[1].split('/')[0]
  } else if (url.includes('twitter.com/') || url.includes('x.com/')) {
    const parts = url.split('/')
    for (const part of parts) {
      if (part && !['twitter.com', 'x.com', 'status', 'https:', ''].includes(part)) {
        return part
      }
    }
  }
  return null
}

// Helper function to get platform info
const getPlatformInfo = (url: string | null) => {
  if (!url) return { name: null, icon: null }

  const platforms = {
    't.me': {
      name: 'Telegram',
      icon: '/telegram.png'
    },
    'twitter.com': {
      name: 'X',
      icon: '/x.png'
    },
    'x.com': {
      name: 'X',
      icon: '/x.png'
    }
  }

  for (const [domain, info] of Object.entries(platforms)) {
    if (url.toLowerCase().includes(domain)) {
      return info
    }
  }

  return { name: null, icon: null }
}

// Add this helper function near the top with other helper functions
const getEmojiColor = (name: string): number => {
  // Extract emoji if it exists at the start of the name
  const emojiMatch = name.match(/^(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])/);
  if (!emojiMatch) return 999; // No emoji, put at the end
  
  const emoji = emojiMatch[0];
  
  // Define color categories
  const emojiColorOrder: { [key: string]: number } = {
    // Black/White emojis
    '⚫': 1, '⚪': 1, '⬛': 1, '⬜': 1, '▪️': 1, '▫️': 1,
    // Red emojis
    '🔴': 2, '❤️': 2, '🟥': 2, '🏮': 2,
    // Orange emojis
    '🟧': 3, '🟠': 3, '🔸': 3,
    // Yellow emojis
    '💛': 4, '🟡': 4, '🟨': 4, '⭐': 4
  };

  return emojiColorOrder[emoji] || 999;
};

export default function Home() {
  const [channels, setChannels] = useState<Channel[]>([])
  const [selectedChannel, setSelectedChannel] = useState<string>('')
  const [timeWindow, setTimeWindow] = useState<number>(24)
  const [loading, setLoading] = useState<boolean>(false)
  const [messages, setMessages] = useState<any[]>([])
  const [selectedImage, setSelectedImage] = useState<{ src: string; alt: string } | null>(null)
  const [selectedVideo, setSelectedVideo] = useState<{ src: string; type: string } | null>(null)

  useEffect(() => {
    fetchChannels()
  }, [])

  const fetchChannels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/channels')
      const data = await response.json()
      setChannels(data)
    } catch (error) {
      console.error('Error fetching channels:', error)
    }
  }

  const handleScrape = async () => {
    if (!selectedChannel) return;
    
    setLoading(true);
    setMessages([]);
    
    try {
        console.log(`Starting scrape for channel ${selectedChannel}, ${timeWindow} hours`);
        
        const response = await fetch('http://localhost:8000/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                channel_id: selectedChannel,
                hours: timeWindow,
            }),
        });
        
        console.log(`Received response with status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`Received ${data.length} messages`);
        setMessages(data);
        
        if (data.length === 0) {
            alert('No messages found in the selected time range');
        }
        
    } catch (error) {
        console.error('Error scraping messages:', error);
        alert(`Error scraping messages: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
        setLoading(false);
    }
  }

  const renderMessage = (msg: any) => {
    const timestamp = new Date(msg.timestamp).toLocaleString()
    let source = null
    let thumbnailUrl = null
    let authorIcon = null

    // Extract source and thumbnail from embeds
    if (msg.embeds?.length > 0) {
      const embed = msg.embeds[0]
      thumbnailUrl = embed.thumbnail?.proxy_url || embed.thumbnail?.url
      authorIcon = embed.author?.proxy_icon_url || embed.author?.icon_url

      // Find source field
      const sourceField = embed.fields?.find(
        (field: any) => field.name?.toLowerCase() === 'source'
      )
      source = sourceField?.value || msg.content
    }

    if (!source && msg.content) {
      source = msg.content
    }

    // Extract URL and platform info
    let url = null
    if (source && source.toLowerCase().includes('http')) {
      const urlStart = source.indexOf('http')
      let urlEnd = source.length
      for (const char of [' ', '\n', ')']) {
        const pos = source.indexOf(char, urlStart)
        if (pos !== -1) {
          urlEnd = Math.min(urlEnd, pos)
        }
      }
      url = source.slice(urlStart, urlEnd)
    }

    const username = url ? extractUsernameFromUrl(url) : null
    const { name: platformName, icon: platformIcon } = getPlatformInfo(url)

    return (
      <div key={msg.id} className="p-6 rounded-xl bg-gray-800/50 backdrop-blur-sm mb-6 border border-gray-700/50 hover:border-gray-600/50 transition-all">
        <div className="flex items-start space-x-4">
          {/* Profile section */}
          {(thumbnailUrl || authorIcon) && (
            <div className="relative">
              <img
                src={authorIcon || thumbnailUrl}
                alt="Profile"
                className="w-12 h-12 rounded-full object-cover ring-2 ring-gray-700"
                onError={(e) => (e.currentTarget.style.display = 'none')}
              />
              {platformIcon && (
                <img
                  src={platformIcon}
                  alt={`${platformName} icon`}
                  className="absolute -bottom-1 -right-1 w-5 h-5 ring-2 ring-gray-800 rounded-full bg-white"
                />
              )}
            </div>
          )}

          <div className="flex-1">
            {/* Header */}
            <div className="flex justify-between items-start mb-3">
              <div>
                {username && (
                  <span className="font-medium text-gray-200">@{username}</span>
                )}
                {url && (
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-sm ml-2 transition-colors"
                  >
                    {url}
                  </a>
                )}
              </div>
              <span className="text-gray-400 text-sm">{timestamp}</span>
            </div>

            {/* Embeds */}
            {msg.embeds?.map((embed: any, index: number) => (
              <div key={index} className="border-l-2 border-gray-600 pl-4 mb-3">
                {embed.title && (
                  <h3 className="font-medium text-gray-200 text-lg mb-2">{embed.title}</h3>
                )}
                {embed.description && (
                  <p className="text-gray-300 mb-3 leading-relaxed">{embed.description}</p>
                )}
                {embed.fields?.map((field: any, fieldIndex: number) => (
                  field.name.toLowerCase() !== 'source' && (
                    <div key={fieldIndex} className="mb-3">
                      <div className="font-medium text-gray-300">{field.name}</div>
                      <div className="text-gray-400 mt-1">{field.value}</div>
                    </div>
                  )
                ))}
              </div>
            ))}

            {/* Updated Attachments section */}
            {msg.attachments?.length > 0 && (
              <div className="grid grid-cols-2 gap-4 mt-4">
                {msg.attachments.map((attachment: any, index: number) => {
                  const isImage = attachment.content_type?.startsWith('image/')
                  const isVideo = attachment.content_type?.startsWith('video/')

                  return (
                    <div key={index} className="relative group">
                      {isImage && (
                        <img
                          src={attachment.url}
                          alt={attachment.filename}
                          className="rounded-lg w-full h-auto cursor-pointer transition-all duration-200 group-hover:ring-2 group-hover:ring-blue-500/50"
                          loading="lazy"
                          onClick={() => setSelectedImage({
                            src: attachment.url,
                            alt: attachment.filename
                          })}
                        />
                      )}
                      {isVideo && (
                        <div 
                          className="cursor-pointer group relative"
                          onClick={() => setSelectedVideo({
                            src: attachment.url,
                            type: attachment.content_type
                          })}
                        >
                          <video
                            className="rounded-lg w-full h-auto ring-1 ring-gray-700 group-hover:ring-2 group-hover:ring-blue-500/50 transition-all duration-200"
                          >
                            <source
                              src={attachment.url}
                              type={attachment.content_type}
                            />
                          </video>
                          {/* Play button overlay */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-12 h-12 rounded-full bg-black/50 flex items-center justify-center group-hover:bg-black/70 transition-colors">
                              <svg 
                                className="w-6 h-6 text-white" 
                                fill="currentColor" 
                                viewBox="0 0 24 24"
                              >
                                <path d="M8 5v14l11-7z" />
                              </svg>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gray-900 text-gray-100">
      <div className="max-w-5xl mx-auto p-6 sm:p-8">
        <h1 className="text-3xl font-bold mb-8 text-center bg-clip-text text-gray-200">
          NewsNow
        </h1>
        
        <div className="space-y-4 mb-8">
          <div className="grid sm:grid-cols-2 gap-4">
            <select
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="w-full p-2.5 rounded-lg bg-gray-800 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500/50 focus:border-transparent outline-none"
            >
              <option value="">Select a feed</option>
              {channels
                .sort((a, b) => {
                  const colorA = getEmojiColor(a.name);
                  const colorB = getEmojiColor(b.name);
                  if (colorA === colorB) {
                    return a.name.localeCompare(b.name);
                  }
                  return colorA - colorB;
                })
                .map((channel) => (
                  <option key={channel.id} value={channel.id}>
                    {channel.name}
                  </option>
                ))}
            </select>

            <select
              value={timeWindow}
              onChange={(e) => setTimeWindow(Number(e.target.value))}
              className="w-full p-2.5 rounded-lg bg-gray-800 border border-gray-700 text-gray-200 focus:ring-2 focus:ring-blue-500/50 focus:border-transparent outline-none"
            >
              <option value={1}>Last hour</option>
              <option value={4}>Last 4 hours</option>
              <option value={8}>Last 8 hours</option>
              <option value={24}>Last 24 hours</option>
            </select>
          </div>

          <button
            onClick={handleScrape}
            disabled={!selectedChannel || loading}
            className="w-full py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
          >
            {loading ? 'Loading...' : 'Load News'}
          </button>
        </div>

        {messages.length > 0 && (
          <div>
            <h2 className="text-xl font-medium text-gray-200 mb-6 flex items-center">
              Updates
              <span className="ml-2 px-2.5 py-0.5 bg-gray-800 text-gray-400 text-sm rounded-full">
                {messages.length}
              </span>
            </h2>
            <div className="space-y-4">
              {messages.map((msg) => renderMessage(msg))}
            </div>
          </div>
        )}
      </div>
      
      {selectedImage && (
        <ImageModal
          src={selectedImage.src}
          alt={selectedImage.alt}
          onClose={() => setSelectedImage(null)}
        />
      )}
      
      {selectedVideo && (
        <VideoModal
          src={selectedVideo.src}
          type={selectedVideo.type}
          onClose={() => setSelectedVideo(null)}
        />
      )}
    </main>
  )
}