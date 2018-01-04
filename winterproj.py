#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 16:07:36 2017

@author: Draper
Function: Creates playlist based on Spotify US Top Charts
"""
import spotipy
import spotipy.util as util

#parameters for client information on Spotify's API
scope = 'user-library-read user-top-read user-follow-read user-read-recently-played playlist-modify-public'
  
with open('credentials.txt', 'r') as f:
    username = str.replace(f.readline(),'\n','')
    clientId = str.replace(f.readline(),'\n','')
    clientSecret = str.replace(f.readline(),'\n','')
    redirect = str.replace(f.readline(),'\n','')
    
    f.close()

#attempts access to Spotify's API - post redirected URL in the console
token = util.prompt_for_user_token(username, scope,
                                   client_id=clientId, 
                                   client_secret=clientSecret,
                                   redirect_uri = redirect)

def main():
    if token: #if access was granted
        #spotify API object 
        sp = spotipy.Spotify(auth=token)
        pList = sp.current_user_top_artists(limit=50, time_range='short_term')
        tList = [a['id'] for a in sp.current_user_top_tracks(limit=50, time_range='short_term')['items']]
        g_dict = {}
        for track in pList['items']:
            for genre in track['genres']:
                if genre not in g_dict:
                    g_dict[genre] = 1
                else:
                    g_dict[genre] += 1
        g_list=[list(g_dict.keys())[list(g_dict.values()).index(x)]for x in sorted(list(g_dict.values()))[-5:]]

        aList = sp.current_user_top_artists(limit=10, time_range='short_term')
        sim_list = []
        for artist in aList['items']:
            for sim_art in sp.artist_related_artists(artist['id'])['artists']:
                if sim_art['name'] not in sim_list:
                    sim_list.append(sim_art['name'])        
        
        query_genre =  ' OR '.join(['genre:' + str.replace(x, ' ','+') for x in g_list])
        
        trackIds = []
        for a in range(len(sim_list)):
            query = 'artist:' + sim_list[a] + ' AND year:2017 AND ' + query_genre
            results = sp.search(query,limit=1, type='track', market='US')
            #print(results)
            if results['tracks']['total'] != 0:
                for songs in results['tracks']['items']:
                    if songs['id'] not in trackIds:
                        trackIds.append(songs['id'])
                        print(songs['name'])

        print('\n')

        #create spotitry playlist if it DOES NOT exist, or update spotitry playlist if it DOES exist
        userPlaylists = sp.current_user_playlists(limit=50, offset=0)
        userPlaylist = {}
        for pls in userPlaylists['items']:
            if pls['name'] not in userPlaylist:
                userPlaylist[pls['name']] = pls['id']

        if str(username + "'s awesome mix vol 1") not in userPlaylist:
            print('Creating',str(username + "'s awesome mix vol 1"))
            playlist1 = sp.user_playlist_create(username, str(username + "'s awesome mix vol 1"), public=True)
            sp.user_playlist_add_tracks(username, playlist1['id'], trackIds[:100], position=None)
        else:
            playlist_id = userPlaylist[str(username + "'s awesome mix vol 1")]
            print(str(username + "'s awesome mix vol 1"),'Already Created')
            print('Updating',str(username + "'s awesome mix vol 1"))
            sp.user_playlist_replace_tracks(username, playlist_id, trackIds[:100])

main()