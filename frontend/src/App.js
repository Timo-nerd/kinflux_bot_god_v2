import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar, Clock, Play, Star, Search, Filter, Tv, Users, Trophy, Globe } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Input } from './components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [matches, setMatches] = useState([]);
  const [leagues, setLeagues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeague, setSelectedLeague] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('live');

  // Mock data for demonstration
  const mockMatches = [
    {
      id: 1,
      homeTeam: 'Manchester United',
      awayTeam: 'Liverpool',
      league: 'Premier League',
      date: '2025-01-20',
      time: '15:00',
      status: 'live',
      score: { home: 2, away: 1 },
      hasHighlights: true,
      isFree: true
    },
    {
      id: 2,
      homeTeam: 'Real Madrid',
      awayTeam: 'Barcelona',
      league: 'La Liga',
      date: '2025-01-20',
      time: '20:00',
      status: 'upcoming',
      score: null,
      hasHighlights: false,
      isFree: true
    },
    {
      id: 3,
      homeTeam: 'Bayern Munich',
      awayTeam: 'PSG',
      league: 'UEFA Champions League',
      date: '2025-01-19',
      time: '21:00',
      status: 'finished',
      score: { home: 3, away: 2 },
      hasHighlights: true,
      isFree: true
    },
    {
      id: 4,
      homeTeam: 'Nigeria',
      awayTeam: 'Morocco',
      league: 'AFCON',
      date: '2025-01-21',
      time: '18:00',
      status: 'upcoming',
      score: null,
      hasHighlights: false,
      isFree: true
    }
  ];

  const mockLeagues = [
    { id: 'premier-league', name: 'Premier League', country: 'England', icon: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
    { id: 'la-liga', name: 'La Liga', country: 'Spain', icon: '🇪🇸' },
    { id: 'champions-league', name: 'UEFA Champions League', country: 'Europe', icon: '🏆' },
    { id: 'world-cup', name: 'FIFA World Cup', country: 'World', icon: '🌍' },
    { id: 'afcon', name: 'AFCON', country: 'Africa', icon: '🌍' }
  ];

  useEffect(() => {
    // Simulate API loading
    setTimeout(() => {
      setMatches(mockMatches);
      setLeagues(mockLeagues);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredMatches = matches.filter(match => {
    const matchesLeague = selectedLeague === 'all' || match.league.toLowerCase().includes(selectedLeague.toLowerCase());
    const matchesSearch = match.homeTeam.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         match.awayTeam.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         match.league.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesStatus = true;
    if (activeTab === 'live') matchesStatus = match.status === 'live';
    else if (activeTab === 'upcoming') matchesStatus = match.status === 'upcoming';
    else if (activeTab === 'finished') matchesStatus = match.status === 'finished';
    
    return matchesLeague && matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'bg-red-500 text-white';
      case 'upcoming': return 'bg-blue-500 text-white';
      case 'finished': return 'bg-gray-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const handleWatchMatch = (match) => {
    if (match.status === 'live' || match.hasHighlights) {
      // This would open a video player with legal content
      alert(`Opening ${match.status === 'live' ? 'live stream' : 'highlights'} for ${match.homeTeam} vs ${match.awayTeam}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl font-semibold">Loading matches...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-r from-green-400 to-blue-500 p-2 rounded-lg">
                <Tv className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">SoccerStream</h1>
                <p className="text-gray-400 text-sm">Premium soccer experience</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
                <Star className="h-4 w-4 mr-2" />
                Favorites
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative h-96 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1522778119026-d647f0596c20?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxzb2NjZXIlMjBzdGFkaXVtfGVufDB8fHx8MTc1NTQ0NzY0Nnww&ixlib=rb-4.1.0&q=85')`
          }}
        >
          <div className="absolute inset-0 bg-black/60"></div>
        </div>
        <div className="relative container mx-auto px-6 h-full flex items-center">
          <div className="max-w-2xl">
            <h2 className="text-5xl font-bold text-white mb-4">
              Watch Premier League,<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
                La Liga & More
              </span>
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Stream live matches, highlights, and replays from the world's top soccer leagues
            </p>
            <div className="flex items-center space-x-4">
              <Button size="lg" className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700">
                <Play className="h-5 w-5 mr-2" />
                Watch Now
              </Button>
              <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10">
                <Calendar className="h-5 w-5 mr-2" />
                View Schedule
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Leagues Section */}
      <section className="py-12 bg-black/20">
        <div className="container mx-auto px-6">
          <h3 className="text-3xl font-bold text-white mb-8 text-center">Featured Leagues</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
            {leagues.map((league) => (
              <Card 
                key={league.id}
                className="bg-white/10 backdrop-blur-lg border-white/20 hover:bg-white/20 transition-all cursor-pointer group"
                onClick={() => setSelectedLeague(league.id)}
              >
                <CardContent className="p-6 text-center">
                  <div className="text-4xl mb-3">{league.icon}</div>
                  <h4 className="text-white font-semibold mb-1">{league.name}</h4>
                  <p className="text-gray-400 text-sm">{league.country}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-12">
        <div className="container mx-auto px-6">
          {/* Search and Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search teams or leagues..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                />
              </div>
            </div>
            <Select value={selectedLeague} onValueChange={setSelectedLeague}>
              <SelectTrigger className="w-48 bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="Select league" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Leagues</SelectItem>
                {leagues.map((league) => (
                  <SelectItem key={league.id} value={league.id}>{league.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Matches Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-white/10 border-white/20">
              <TabsTrigger value="live" className="data-[state=active]:bg-red-500 data-[state=active]:text-white">
                Live Matches
              </TabsTrigger>
              <TabsTrigger value="upcoming" className="data-[state=active]:bg-blue-500 data-[state=active]:text-white">
                Upcoming
              </TabsTrigger>
              <TabsTrigger value="finished" className="data-[state=active]:bg-gray-500 data-[state=active]:text-white">
                Previous Matches
              </TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredMatches.map((match) => (
                  <Card key={match.id} className="bg-white/10 backdrop-blur-lg border-white/20 hover:bg-white/20 transition-all">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <Badge className={getStatusColor(match.status)}>
                          {match.status.toUpperCase()}
                        </Badge>
                        {match.isFree && (
                          <Badge variant="outline" className="border-green-400 text-green-400">
                            FREE
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-white text-lg">
                        {match.homeTeam} vs {match.awayTeam}
                      </CardTitle>
                      <CardDescription className="text-gray-300">
                        {match.league} • {match.date} {match.time}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {match.score && (
                        <div className="text-center mb-4">
                          <div className="text-3xl font-bold text-white">
                            {match.score.home} - {match.score.away}
                          </div>
                        </div>
                      )}
                      <div className="flex gap-2">
                        {match.status === 'live' && (
                          <Button 
                            className="flex-1 bg-red-600 hover:bg-red-700"
                            onClick={() => handleWatchMatch(match)}
                          >
                            <Play className="h-4 w-4 mr-2" />
                            Watch Live
                          </Button>
                        )}
                        {match.hasHighlights && (
                          <Button 
                            variant="outline" 
                            className="flex-1 border-white/30 text-white hover:bg-white/10"
                            onClick={() => handleWatchMatch(match)}
                          >
                            <Tv className="h-4 w-4 mr-2" />
                            Highlights
                          </Button>
                        )}
                        {match.status === 'upcoming' && (
                          <Button 
                            variant="outline" 
                            className="flex-1 border-white/30 text-white hover:bg-white/10"
                          >
                            <Clock className="h-4 w-4 mr-2" />
                            Set Reminder
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              
              {filteredMatches.length === 0 && (
                <div className="text-center py-12">
                  <div className="text-gray-400 text-lg">No matches found</div>
                  <p className="text-gray-500 mt-2">Try adjusting your search or filters</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black/40 backdrop-blur-lg border-t border-white/10 py-12">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="bg-gradient-to-r from-green-400 to-blue-500 p-2 rounded-lg">
                  <Tv className="h-6 w-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white">SoccerStream</span>
              </div>
              <p className="text-gray-400">
                Your ultimate destination for premium soccer streaming experience.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Leagues</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Premier League</li>
                <li>La Liga</li>
                <li>UEFA Champions League</li>
                <li>World Cup</li>
                <li>AFCON</li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Live Streaming</li>
                <li>Match Highlights</li>
                <li>Previous Matches</li>
                <li>Match Schedules</li>
                <li>Free Content</li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Terms of Service</li>
                <li>Privacy Policy</li>
                <li>Content Licensing</li>
                <li>Support</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 SoccerStream. All rights reserved. Content is aggregated from legal sources.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;