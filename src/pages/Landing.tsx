
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Sparkles, Star, Sun } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import OmLogo from '../components/OmLogo';

gsap.registerPlugin(ScrollTrigger);

const Landing = () => {
  const heroRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Generate random stars
  const [stars, setStars] = useState<Array<{ id: number; x: number; y: number; size: number; delay: number }>>([]);
  


  useEffect(() => {
    // Generate more stars for better effect
    const newStars = Array.from({ length: 80 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 1,
      delay: Math.random() * 4
    }));
    setStars(newStars);

    // Hero text entrance animation
    if (heroRef.current) {
      gsap.fromTo(heroRef.current.children, {
        opacity: 0,
        y: 60,
        scale: 0.95
      }, {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 1.5,
        stagger: 0.3,
        ease: "power3.out"
      });
    }

  }, []);

  const handleChatClick = () => {
    // Simple button animation without page fade
    const button = document.querySelector('.chat-button');
    if (button) {
      gsap.to(button, {
        scale: 0.95,
        duration: 0.1,
        yoyo: true,
        repeat: 1,
        onComplete: () => {
          // Navigate immediately without fading the page
          navigate('/chat');
        }
      });
    } else {
      navigate('/chat');
    }
  };

  return (
    <div className="page-transition-container min-h-screen bg-gradient-to-br from-slate-800 via-blue-900 to-blue-800 text-white relative overflow-hidden">
      <Header />
      
      {/* Enhanced Animated Stars Background */}
      <div className="absolute inset-0 overflow-hidden">
        {stars.map(star => (
          <div
            key={star.id}
            className="absolute bg-blue-200/70 rounded-full animate-pulse twinkle-animation"
            style={{
              left: `${star.x}%`,
              top: `${star.y}%`,
              width: `${star.size}px`,
              height: `${star.size}px`,
              animationDelay: `${star.delay}s`,
              animationDuration: `${2 + Math.random() * 3}s`,
              boxShadow: `0 0 ${star.size * 2}px rgba(147, 197, 253, 0.3)`
            }}
          />
        ))}
      </div>

      {/* Enhanced light effects */}
      <div className="absolute bottom-0 left-0 right-0 h-96 bg-gradient-to-t from-blue-400/10 via-blue-300/5 to-transparent" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-0 left-1/4 w-full h-32 bg-gradient-to-r from-blue-400/10 via-blue-500/20 to-blue-600/10 blur-2xl transform rotate-12" />
      
             {/* Main Landing Content */}
       <div className="main-content relative z-10 min-h-screen flex items-center justify-center px-6">
        <div className="text-center max-w-5xl mx-auto">
          <div ref={heroRef}>
            <h1 className="text-6xl md:text-7xl lg:text-8xl font-light mb-8 leading-tight tracking-tight bg-gradient-to-r from-blue-200 via-blue-300 to-blue-400 bg-clip-text text-transparent">
              Pandit Pradeep Kiradoo
            </h1>
            
            <p className="text-lg md:text-xl mb-12 text-blue-100/80 font-light max-w-2xl mx-auto">
              Complete Vedic Astrology Guidance for Life's Journey
            </p>

            {/* Welcome Message */}
            <Card className="bg-blue-900/20 backdrop-blur-xl border border-blue-300/20 p-8 max-w-3xl mx-auto mb-8 hover:bg-blue-900/30 transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl cosmic-glow">
              <div className="flex items-center justify-center space-x-3 mb-4">
                <Star className="w-8 h-8 text-yellow-300 animate-pulse" />
                <OmLogo size={32} className="text-blue-300" />
                <Sun className="w-8 h-8 text-orange-300 animate-pulse" />
              </div>
              <h2 className="text-2xl font-semibold text-blue-200 mb-4">
                Welcome to Vedic Astrology Consultation
              </h2>
                             <p className="text-blue-100/90 leading-relaxed mb-6">
                 Discover the cosmic influences shaping your life through the ancient wisdom of Vedic astrology. 
                 Chat directly with Pandit Pradeep Kiradoo for instant guidance and personalized insights.
               </p>
                               <p className="text-blue-100/80 text-sm">
                  Click "Chat with Pandit Ji" to start your consultation. Ask about your birth chart, planetary influences, or any life concerns.
                </p>
            </Card>

                         {/* Navigation Buttons */}
            <div className="flex justify-center space-x-6 flex-wrap gap-4">
               <Button 
                 onClick={handleChatClick}
                 className="chat-button bg-gradient-to-r from-purple-500/80 to-blue-500/80 hover:from-purple-600/90 hover:to-blue-600/90 text-white px-8 py-3 border-0 hover:scale-105 transition-all duration-300 hover:shadow-lg"
               >
                 <Sparkles className="w-5 h-5 mr-2" />
                 Chat with Pandit Ji
               </Button>
              <Link to="/about">
                <Button variant="outline" className="border-blue-300/40 text-blue-100/90 hover:bg-blue-800/20 hover:text-blue-100 px-8 py-3 bg-transparent hover:scale-105 transition-all duration-300">
                   Learn More
                </Button>
              </Link>
            </div>

                         {/* Features Preview */}
             <div className="grid md:grid-cols-3 gap-6 mt-16 max-w-4xl mx-auto">
               <Card className="bg-blue-900/20 backdrop-blur-xl border border-blue-300/20 p-6 text-center hover:transform hover:scale-105 transition-all duration-300 hover:bg-blue-900/30 cosmic-glow">
                 <Star className="w-12 h-12 text-yellow-400 mb-4 mx-auto animate-pulse" />
                 <h3 className="text-xl font-semibold mb-3 text-blue-100">Instant Chat</h3>
                 <p className="text-sm text-blue-100/80">Get immediate answers and guidance from Pandit Pradeep Kiradoo</p>
               </Card>
               
               <Card className="bg-blue-900/20 backdrop-blur-xl border border-blue-300/20 p-6 text-center hover:transform hover:scale-105 transition-all duration-300 hover:bg-blue-900/30 cosmic-glow">
                 <OmLogo size={48} className="text-blue-400 mb-4 mx-auto" />
                 <h3 className="text-xl font-semibold mb-3 text-blue-100">Vedic Wisdom</h3>
                 <p className="text-sm text-blue-100/80">Ancient Jyotish Shastra insights for modern life challenges</p>
               </Card>
               
               <Card className="bg-blue-900/20 backdrop-blur-xl border border-blue-300/20 p-6 text-center hover:transform hover:scale-105 transition-all duration-300 hover:bg-blue-900/30 cosmic-glow">
                 <Sun className="w-12 h-12 text-orange-400 mb-4 mx-auto animate-pulse" />
                 <h3 className="text-xl font-semibold mb-3 text-blue-100">24/7 Available</h3>
                 <p className="text-sm text-blue-100/80">Chat anytime, anywhere for personalized astrological guidance</p>
               </Card>
                    </div>
                  </div>
                </div>
              </div>
       

    </div>
  );
};

export default Landing;
