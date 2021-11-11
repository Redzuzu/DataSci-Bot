from os import times
import discord
from discord.ext import commands
import yt_dlp
import json
import asyncio
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from datetime import datetime, timedelta
import math
from discord.ext import menus







class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""

    def __init__(self, queue, *, per_page=5):
        super().__init__(queue, per_page=per_page)
        self.queue = queue

    async def format_page(self, menu: menus.Menu, page):
        lis= []
        lis = self.queue
        pageNum=math.ceil(lis.index(page[0])/5)+1
        #print('this is next page \n\n\n\n')
        #print(page)
        #print(len(page))
        #print()
        embed = discord.Embed(title='Queue for server', colour=0xc40b0b)
        desc=f'```Queue length: {str(len(lis))}\n\n'
        for i,song in enumerate(page):
            desc+=f'#{str(lis.index(page[i])+1)} {song["title"]} ({song["duration"]})\n'
        desc+='```'

        embed.description=desc
        # try:
        #     embed.add_field(name='title', value=f'{page[0]["title"]}')
        #     embed.add_field(name='title', value=f'{page[1]["title"]}')
        # except:
        #     print('missing page shit thiem idk')
        #     pass
        # embed.add_field(name='title', value=f'{page[2]["title"]}')
        # embed.add_field(name='title', value=f'{page[3]["title"]}')
        # embed.add_field(name='title', value=f'{page[4]["title"]}')

        
        embed.set_footer(text=f"Page {str(pageNum)}/" + str(math.ceil(len(lis)/5)))

        return embed

    def is_paginating(self):
        # We always want to embed even on 1 page of results...
        return True






client_credentials_manager = SpotifyClientCredentials(client_id=config('spotify_client_id'), client_secret=config('spotify_client_secret'))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API




class Queue:
    def __init__(self):
        self.songs = []
        self.nowPlaying=None
        self.volume=1.0
        self.loop =False
        self.queueInfo={}
        self.queueIndex=0
        self.ytSearch=False
        self.youtubePlaylist=False
        self.youtubeUrl=False
    
    def nextSong(self):
        self.songs.pop(0)
        return self.songs

    def shuffle(self):
        random.shuffle(self.songs)

    def isEmpty(self):
        return self.songs == []
    
    def enqueue(self, song):
        self.songs.append(song)

    def playlistEnqueue(self, playlist):
        for x in playlist:
            
            self.songs.append('https://www.youtube.com/watch?v='+x['id'])

    def indexEnqueue(self, song, index):
        self.songs.insert(index-1, song)

    def clearQueue(self):
        self.songs.clear()
        self.nowPlaying='None'
        self.volume=1.0
        self.loop =False
        self.queueInfo={}
        self.queueIndex=0

    def removeFromQueue(self, index:int):
        print(f'before lsit remove{self.songs}')
        song = None
        if index !=1:
            song =self.songs.pop(index-1)
        else:
            #song =self.songs[index-1]
            song =self.songs.pop(index-1)
            
        print(f'removed from song list {self.songs}')
        return song 


    def size(self):
        return len(self.songs)
    
    def getQueue(self):
        return self.songs
    

masterList={}

class newMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Queue=None

    ''' 
    queue
    Requirments
    1. add songs  +
    2. play multiple songs one after another +
    3. skip songs +
    4. remove songs +
    5. add inbwetween songs +
    6. loop +
    7. add youtlbe playlists +
    9. Shuffle +
    8. spotuifly?+
    9. current time in song
    10. per song volume
    11. doesnt work if in different voice channel
    12. bug in seek command on large songs? 
    13. leaving vc breakes queue and playing songs (need to clean up before/after leave)
    
    
    '''

    '''
    get current voice channel
    voice client
    next song
    '''
#  THIS IS ALL SHIT; NEED TO FIX ASYNC/SYNC, SHOULD BE USING PCM FOR GODS SAKE
    async def _play_song(self, ctx, state, url,timestamp=0):
        
       # source = discord.PCMVolumeTransformer(
       #     discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)

        #vc =ctx.message.author.voice.channel
            

        guildQueue= masterList[ctx.guild.id]
        def after_playing(err):
            guildQueue= masterList[ctx.guild.id]
            print(guildQueue.queueIndex)
            if guildQueue.queueIndex < guildQueue.size():

                songs = guildQueue.getQueue()

                #print(songs[guildQueue.queueIndex])
                #print(guildQueue.getQueue())
                asyncio.run_coroutine_threadsafe(self._play_song(ctx, state, songs[guildQueue.queueIndex]),self.bot.loop).result()
                
                embed =  discord.Embed(title=f'Playing {guildQueue.nowPlaying}',  description='song playing', colour = 0xc40b0b, timestamp =datetime.utcnow())
                embed.add_field(name='link', value=songs[guildQueue.queueIndex]['url'])
                embed.add_field(name='Title', value=f"[{songs[guildQueue.queueIndex]['title']}]({songs[guildQueue.queueIndex]['url']})")
                embed.add_field(name='channel', value=songs[guildQueue.queueIndex]['channel'])
                embed.add_field(name='length', value=str(timedelta(seconds=int(songs[guildQueue.queueIndex]['duration']))))

                asyncio.run_coroutine_threadsafe(ctx.send(embed=embed),self.bot.loop).result()
                guildQueue.queueIndex +=1


            else:
                guildQueue.queueIndex=0
                if guildQueue.loop:
                    
                    #print(guildQueue.getQueue())
                    songs = guildQueue.getQueue()
                   #self._play_song(ctx, guildQueue,songs[guildQueue.queueIndex])
                    asyncio.run_coroutine_threadsafe(self._play_song(ctx, state, songs[guildQueue.queueIndex]),self.bot.loop).result()

                    #print('called play song in loop')
                    guildQueue.queueIndex +=1
                    #print(guildQueue.getQueue())
                    print(guildQueue.queueIndex)
                    #print('inloop')
                else:
                    guildQueue.clearQueue()
                #print('dooning quweu')
                asyncio.run_coroutine_threadsafe(ctx.send('done queue'),self.bot.loop)
                #guildQueue.queueIndex=0
            
        
        
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':f'-vn -ss {timestamp}'}    
        YDL_OPTIONS ={'format':"bestaudio",'source_address': '0.0.0.0'}        
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                _Queue= masterList[ctx.guild.id]  
                
                print(url)
                '''
                if 'spotify' in url:
                    _Queue.removeFromQueue(_Queue.queueIndex+1)
                    print(url)
                    spotList=[]
                    if '/track/' in url:
                        spotDictTemp={}
                        result= sp.track(url)
                        
                        name = result['name']
                        spotDictTemp['name'] =result['name']
                        spotDictTemp['artist']=result['album']['artists'][0]['name']
                        spotDictTemp['ytsearch']= 'ytsearch:'+result['name']+' by '+result['album']['artists'][0]['name']
                        spotList.append(spotDictTemp)
                    elif '/playlist/'in url:
                        playlist=sp.playlist(url)
                        
                        for result in playlist['tracks']['items']:
                            result =result['track']
                            name = result['name']
                            spotDictTemp={}
                            spotDictTemp['name'] =result['name']
                            spotDictTemp['artist']=result['album']['artists'][0]['name']
                            spotDictTemp['ytsearch']= 'ytsearch:'+result['name']+' by '+result['album']['artists'][0]['name']
                            spotList.append(spotDictTemp)
                    
                    elif '/album/'in url:
                        album=sp.album(url)
                        
                        for result in album['tracks']['items']:
                            spotDictTemp={}
                            name = result['name']
                            spotDictTemp['name'] =result['name']
                            spotDictTemp['artist']=result['artists'][0]['name']
                            spotDictTemp['ytsearch']= 'ytsearch:'+result['name']+' by '+result['artists'][0]['name']
                            spotList.append(spotDictTemp)
                    
                    print(json.dumps(spotList,indent=4))

                    for y in spotList:

                        print(y)
                            
                        _Queue.enqueue(y['ytsearch'])
                        print('test')
                    
                    url=spotList[0]['ytsearch']
                
                print(f'THIS IS UR: FPR YDL{url}')
                info = ydl.extract_info(url, download=False)
                #print(info)
                
                #print(info['channel'])# youtube
                #print(info['uploader']) # soundcloud
                #print(info['duration'])

                if 'ytsearch' in url: 
                    _Queue.ytSearch=True
                
                if _Queue.ytSearch:
                    url2= info['entries'][0]['url']
                    print(info['entries'][0]['title'])
                    print(info['entries'][0]['duration'])
                    _Queue.ytSearch=False
                else:                
                    if _Queue.youtubePlaylist:
                        url = 'https://youtu.be/'+info['entries'][0]['id']
                        
                       #print(info['entries'][0]['id'])
                        #print(url2)
                        for x in info['entries']:
                            print(x['id'])
                        _Queue.playlistEnqueue(info['entries'])
                        info = ydl.extract_info(url, download=False)
                        url2 = info['formats'][0]['url']
                        

                        #url2 =  _Queue.getQueue()[_Queue.queueIndex]
                        _Queue.youtubePlaylist=False
                    else:
                        
                        url2 = info['formats'][0]['url']
                        #print(info['formats'][0])
                '''
            
            # conversion = datetime.timedelta(seconds=info['duration'])
                #dur = conversion.strftime('%H:%M:%S')
                #source = asyncio.run_coroutine_threadsafe(discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS),self.bot.loop).result()
                #source = asyncio.gather(source1)
                #print(url2)

                if url['direct']:
                    url2 = url['url']
                else:
                    info = ydl.extract_info(url['url'], download=False)
                    url2 = info['formats'][0]['url']


                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS), volume=1.0)
                
                if ctx.voice_client.is_playing():
                    ctx.voice_client.source = source
                else:

                    ctx.voice_client.play(source, after=after_playing)
                _Queue.nowPlaying = url['title']
            except Exception as e:
                raise e
                print(e)
                print("erorerproro")
                print(_Queue.getQueue())
                _Queue.getQueue().pop(0)
                print(_Queue.getQueue())

                # do i need this???
                try:
                    _Queue.nowPlaying = _Queue.getQueue()[_Queue.queueindex]
                except:
                    
                    pass
                _Queue.ytSearch=False
                #_Queue.playlist=False
            #embed =  discord.Embed(title=info['title'], url=url,colour = 0xc40b0b, timestamp = datetime.datetime.utcnow())
            #embed.add_field(name='Duration:', value=str(conversion))
                
        #await .send(embed=embed)



    # def afterSong(error):


        
    #     fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
    #     try:
    #         fut.result()
    #     except:
    #         print(f'error playing song: {error}')
    #         pass

    @commands.command(aliases=['sh'])
    async def shuffle(self,ctx):
        guildQueue= masterList[ctx.guild.id]
        guildQueue.shuffle()
        await ctx.send('Queue shuffled')


    @commands.command(aliases=['l'])
    async def loop(self,ctx):
        guildQueue= masterList[ctx.guild.id]
        guildQueue.loop= not guildQueue.loop
        if guildQueue.loop:
            await ctx.send('**Queue looping Enabled**')
        else:
            await ctx.send('**Queue looping Disabled**')

    @commands.command(aliases=['in'])
    async def insert(self,ctx, url ,index: int):
        guildQueue= masterList[ctx.guild.id]
        await ctx.send(f'Queued `{guildQueue.indexEnqueue(url,index)}` at postition {index}')


    @commands.command(aliases=['q'])
    async def queue(self,ctx):
        guildQueue= masterList[ctx.guild.id]
        pages = PaginatorSource(queue=guildQueue.getQueue())
        paginator = menus.MenuPages(source=pages, timeout=180, delete_message_after=False)

        await paginator.start(ctx)
        #await ctx.send(f'Current song is {guildQueue.nowPlaying}\nCurrent queue is `{guildQueue.getQueue()}`')
    
    @commands.command(aliases=['r'])
    async def remove(self,ctx, index: int):
        guildQueue= masterList[ctx.guild.id]
        print(f'removed {guildQueue.getQueue()[index-1]}')
        if index ==1:
            ctx.voice_client.stop()
        await ctx.send(f'Removed `{guildQueue.removeFromQueue(index)}` from the queue')

    @commands.command(aliases=['c'])
    async def clear(self,ctx):
        guildQueue= masterList[ctx.guild.id]
        guildQueue.clearQueue()
        ctx.voice_client.stop()
        await ctx.send('Cleared Queue!')

    @commands.command(aliases=['j'])
    async def join(self,ctx):
        if ctx.author.voice.channel is None:
            await ctx.send("you are not in a voice channel")
        voiceChannel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voiceChannel.connect()
        else:
            await ctx.voice_client.move_to(voiceChannel)
    
    @commands.command(aliases=['le'])
    async def leave(self,ctx):
        await ctx.voice_client.disconnect()

    @commands.command(aliases=['p'])
    async def play(self,ctx,*,url=None):
        # filter out ytsearch vs links
        # v2 should get meta-data before calling _play_song()

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        if url == None:
            #move from paused to play 
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                await ctx.send('resumed')
        else:
            YDL_OPTIONS ={'format':"bestaudio",'source_address': '0.0.0.0'}        
            ydl=yt_dlp.YoutubeDL(YDL_OPTIONS)
            guildQueue=None
            if ctx.guild.id not in masterList.keys():
                self.Queue = Queue()
                masterList[ctx.guild.id] = self.Queue
                guildQueue= masterList[ctx.guild.id]
                guildQueue.queueIndex=0
        
            elif ctx.guild.id in masterList.keys():
                guildQueue= masterList[ctx.guild.id]

            if 'http' in url:
                #url is passed as argument



                #if 'https://www.youtube.com/playlist?' in url:
                print(url)
                if 'https://www.youtube.com/' in url or 'https://youtu.be/' in url:
                    if 'list=' in url:
                    
                        guildQueue.youtubePlaylist=True
                        
                        info = ydl.extract_info(url, download=False)
                        
                        for info in info['entries']:
                            tempDict={}
                            tempDict['url']='https://www.youtube.com/watch?v='+info['id']
                            tempDict['title']= info['title']
                            tempDict['channel']=info['channel']
                            tempDict['duration']=info['duration']
                            tempDict['direct']=False
                            guildQueue.enqueue(tempDict)

                    else:
                        print('\n\nNOT PLAYLIST\n\n')
                        info = ydl.extract_info(url, download=False)
                        tempDict={}
                        tempDict['url']=url
                        tempDict['title']= info['title']
                        tempDict['channel']=info['channel']
                        tempDict['duration']=info['duration']
                        tempDict['direct']=False
                        guildQueue.enqueue(tempDict)
                        guildQueue.youtubeUrl=True
                        # normal youtbe url

                elif 'spotify' in url:
                    #guildQueue.enqueue(url)
                    await ctx.send('WARNING using spotify metadata to search on youtube')
                    spotList=[]
                    if '/track/' in url:
                        spotDictTemp={}
                        result= sp.track(url)                        
                        spotDictTemp['name'] =result['name']
                        spotDictTemp['artist']=result['album']['artists'][0]['name']
                        spotDictTemp['ytsearch']= 'ytsearch:'+result['name']+' by '+result['album']['artists'][0]['name']
                        spotList.append(spotDictTemp)
                    elif '/playlist/'in url:
                        playlist=sp.playlist(url)
                        
                        for result in playlist['tracks']['items']:
                            result =result['track']
                            spotDictTemp={}
                            spotDictTemp['name'] =result['name']
                            spotDictTemp['artist']=result['album']['artists'][0]['name']
                            spotDictTemp['ytsearch']= 'ytsearch:'+result['name']+' by '+result['album']['artists'][0]['name']
                            spotList.append(spotDictTemp)
                    
                    elif '/album/'in url:
                        album=sp.album(url)
                        
                        for result in album['tracks']['items']:
                            spotDictTemp={}
                            spotDictTemp['name'] =result['name']
                            spotDictTemp['artist']=result['artists'][0]['name']
                            spotDictTemp['ytsearch']= 'ytsearch:'+result['name']+' by '+result['artists'][0]['name']
                            spotList.append(spotDictTemp)
                    
                    print(json.dumps(spotList,indent=4))

                    for y in spotList:
                        tempDict={}
                        #print(y)
                        info = ydl.extract_info(y['ytsearch'], download=False)
                        
                        
                        #tempDict['channel']=info['channel']
                        #tempDict['title']=info['title']
                        tempDict['url']= 'https://www.youtube.com/watch?v='+ info['entries'][0]['id']
                        tempDict['title']= info['entries'][0]['title']
                        tempDict['channel']=info['entries'][0]['channel']
                        tempDict['duration']=info['entries'][0]['duration']
                        tempDict['direct']=False
                        #print(json.dumps(tempDict,indent=4))
                        guildQueue.enqueue(tempDict)
                        print('test')
                    
                        url=tempDict

                        #spotify
                
                elif 'soundcloud' in url:
                    info = ydl.extract_info(url, download=False)
                    
                    tempDict={}
                    tempDict['url']=url
                    tempDict['title']= info['title']
                    tempDict['channel']= info['uploader'] # soundcloud 
                    tempDict['duration']=info['duration']
                    tempDict['direct']=False
                    guildQueue.enqueue(tempDict)
                elif url.endswith(('.mp3','mp4','.mov')):
                    name = url.split('/')[-1].split(".")[0]
                    guildQueue.enqueue({'url':url,'title':name,'channel':'Direct Link','duration':0,'direct':True})
                else:
                    guildQueue.enqueue({'url':url,'title':None,'channel':None,'duration':0,'direct':False})
            else:
                #multi space string is passed --> youtube search
                url = "ytsearch:"+url
                
                info = ydl.extract_info(url, download=False)
                tempDict={}
                tempDict['url']= 'https://www.youtube.com/watch?v='+ info['entries'][0]['id']
                tempDict['title']= info['entries'][0]['title']
                tempDict['channel']=info['entries'][0]['channel']
                tempDict['duration']=info['entries'][0]['duration']         
                tempDict['direct']=False

                guildQueue.enqueue(tempDict)
                #youtube search


            if ctx.voice_client.is_playing():
                await ctx.send(f'Added {url} to queue')
            else:
                # where 
                await self._play_song(ctx, guildQueue, guildQueue.getQueue()[guildQueue.queueIndex])
                
                songs = guildQueue.getQueue()

                
                #print(songs)
                # removed shit here
                print('\nplaying song now\n')
                embed =  discord.Embed(title=f'Playing {guildQueue.nowPlaying}',  description=str(timedelta(seconds=int(songs[guildQueue.queueIndex]['duration']))), colour = 0xc40b0b, timestamp =datetime.utcnow())
                embed.add_field(name='Title', value=f"[{songs[guildQueue.queueIndex]['title']}]({songs[guildQueue.queueIndex]['url']})")
                embed.add_field(name='Channel', value=songs[guildQueue.queueIndex]['channel'])
                await ctx.send(embed=embed)
                guildQueue.queueIndex +=1
                
#-----------------------------------------------------------------------------------
    '''


        h= 'http'
        if url != None and h not in url:
            print(f'non -link {url}')
            url = "ytsearch:"+url
            
            if ctx.guild.id not in masterList.keys():
                self.Queue = Queue()
                masterList[ctx.guild.id] = self.Queue
                print(masterList)
                guildQueue= masterList[ctx.guild.id]
                guildQueue.enqueue(url)
                print(guildQueue.getQueue())
                guildQueue.ytSearch=True
            else:
                guildQueue= masterList[ctx.guild.id]
                guildQueue.enqueue(url)
                print(guildQueue.getQueue())
                guildQueue.ytSearch=True   

        else:
            if url is not None:
                print(ctx.guild.id)
                

                if ctx.guild.id not in masterList.keys():
                    self.Queue = Queue()
                    masterList[ctx.guild.id] = self.Queue
                    print(masterList)
                    guildQueue= masterList[ctx.guild.id]
                    if 'https://www.youtube.com/playlist?' in url:
                        guildQueue.youtubePlaylist=True
                        # fix me (need to get better queud style)
                    else:
                        guildQueue.enqueue(url)
                        print(guildQueue.getQueue())
                else:
                    guildQueue= masterList[ctx.guild.id]
                    if 'https://www.youtube.com/playlist?' in url:
                        guildQueue.youtubePlaylist=True
                    else:
                        guildQueue.enqueue(url)
                        print(guildQueue.getQueue())               


        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('resumed')            

        elif ctx.voice_client.is_playing() and url != None:
            await ctx.send('Added to the Queue')
            #print(ctx.voice_client.source)

        elif url != None:
            #await ctx.trigger_typing()
            """
            FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}    
            YDL_OPTIONS ={'format':"bestaudio",'source_address': '0.0.0.0'}
            vc =ctx.message.author.voice.channel
            
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']

                conversion = datetime.timedelta(seconds=info['duration'])
                #dur = conversion.strftime('%H:%M:%S')

                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source,after=afterSong)
            """
            guildQueue = masterList[ctx.guild.id]
            self._play_song(ctx, guildQueue, url)
            guildQueue.queueIndex +=1
            await ctx.send(f'Playing `{guildQueue.nowPlaying}`')

    '''

    """
    @commands.command()
    async def seek(self,ctx,timestamp):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            ctx.voice_client.play(source)

        else:
            ctx.send('im not palying anything')
    """
    @commands.command()
    async def seek(self,ctx,timestamp: int):
        print(timestamp)

        '''
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':f'-vn -ss {timestamp}'}    
        YDL_OPTIONS ={'format':"bestaudio",'source_address': '0.0.0.0'}        
        ydl=yt_dlp.YoutubeDL(YDL_OPTIONS)

        guildQueue= masterList[ctx.guild.id]
        #print(guildQueue.getQueue())
        #print(guildQueue.queueIndex)
        url=guildQueue.getQueue()[guildQueue.queueIndex-1]
        if url['direct']:
            url2 = url['url']
        else:
            info = ydl.extract_info(url['url'], download=False)
            url2 = info['formats'][0]['url']

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS), volume=1.0)
    
        ctx.voice_client.play(source, after= asyncio.run_coroutine_threadsafe(self._play_song(ctx, guildQueue, guildQueue.getQueue()[guildQueue.queueIndex-1]), self.bot.loop).result())
        guildQueue.nowPlaying = url['title']        
        '''
        guildQueue= masterList[ctx.guild.id]

        
        await self._play_song(ctx, guildQueue, guildQueue.getQueue()[guildQueue.queueIndex-1],timestamp)



        await ctx.send(f"Seeked to {timestamp}")

    
    @commands.command(aliases=['stop','pa'])
    async def pause(self,ctx):
        ctx.voice_client.pause()
        await ctx.send("paused")

    @commands.command(aliases=['res'])
    async def resume(self,ctx):
        ctx.voice_client.resume()
        await ctx.send("resumed")

    '''
    @commands.command(aliases=['skip','s','fs'])
    async def stop(self,ctx):
        ctx.voice_client.stop()
        await ctx.send("stoped")
    '''
    # need to make a real skip command
    @commands.command(aliases=['s','fs'])
    async def skip(self,ctx):

        ctx.voice_client.stop()
        await ctx.send("skiped")

    #needs to be pcm
    @commands.command(aliases=['vol'])
    async def volume(self,ctx,volume):
        new_volume = float(volume)
        voice = ctx.author.voice.channel
        source =  ctx.voice_client.source
        print(source)
        if 0 <= new_volume :#<= 300
            new_volume = new_volume / 100
            source.volume = new_volume
            await ctx.channel.send(f'New Volume {volume}')
        else:
            await ctx.channel.send('Please enter a volume above 0')
            

        
        #source = discord.PCMVolumeTransformer(source)
        

       # ctx.voice_client.stop()
      #  ctx.voice_client.play(source)
        
def setup(bot):
    bot.add_cog(newMusic(bot))