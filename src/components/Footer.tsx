
import { Award, BookOpen, Clock, Heart, Mail, MapPin, Phone, Star, Sun } from 'lucide-react';
import { Link } from 'react-router-dom';
import OmLogo from './OmLogo';

const Footer = () => {
  return (
    <footer className="relative z-10 bg-black/20 backdrop-blur-xl border-t border-white/10 mt-20">
      <div className="container mx-auto px-6 py-16">
        <div className="grid lg:grid-cols-5 md:grid-cols-3 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2 md:col-span-3">
            <div className="flex items-center space-x-2 mb-6">
              <OmLogo size={40} className="text-yellow-400" />
              <span className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-purple-400 bg-clip-text text-transparent">
                Pandit Pradeep Kiradoo
              </span>
            </div>
            <p className="text-purple-200 mb-6 max-w-lg leading-relaxed">
              Renowned Vedic Astrologer with 15+ years of experience in Jyotish Shastra. Bridging ancient wisdom with modern understanding to illuminate your path through cosmic insights and planetary analysis.
            </p>
            <div className="flex items-center space-x-2 text-purple-300 mb-4">
              <Heart className="w-4 h-4 text-pink-400" />
              <span className="text-sm italic">"Bhagya badla nahi ja sakta, par sawara ja sakta hai"</span>
            </div>
            <div className="flex items-center space-x-2 text-purple-300">
              <Award className="w-4 h-4 text-green-400" />
              <span className="text-sm">Certified Vedic Astrology Practitioner</span>
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
              <Phone className="w-5 h-5 mr-2 text-green-400" />
              Get in Touch
            </h3>
            <ul className="space-y-4 text-purple-200">
              <li className="flex items-start space-x-3">
                <Phone className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                <div>
                  <p className="font-medium text-white">Phone</p>
                  <p className="text-sm">Available on request</p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <Mail className="w-4 h-4 text-blue-400 mt-1 flex-shrink-0" />
                <div>
                  <p className="font-medium text-white">Email</p>
                  <p className="text-sm">Contact through consultation form</p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <MapPin className="w-4 h-4 text-red-400 mt-1 flex-shrink-0" />
                <div>
                  <p className="font-medium text-white">Location</p>
                  <p className="text-sm">Online consultations available</p>
                  <p className="text-sm">Worldwide service</p>
                </div>
              </li>
            </ul>
          </div>

          {/* Services */}
          <div>
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
              <Star className="w-5 h-5 mr-2 text-yellow-400" />
              Services
            </h3>
            <ul className="space-y-3 text-purple-200">
              <li className="flex items-center space-x-2 hover:text-yellow-400 transition-colors">
                <Star className="w-3 h-3 text-yellow-400" />
                <span>Birth Chart Analysis</span>
              </li>
              <li className="flex items-center space-x-2 hover:text-yellow-400 transition-colors">
                <Sun className="w-3 h-3 text-orange-400" />
                <span>Career Guidance</span>
              </li>
              <li className="flex items-center space-x-2 hover:text-yellow-400 transition-colors">
                <OmLogo size={12} className="text-purple-400" animated={false} />
                <span>Relationship Compatibility</span>
              </li>
              <li className="flex items-center space-x-2 hover:text-yellow-400 transition-colors">
                <Heart className="w-3 h-3 text-pink-400" />
                <span>Marriage Consultation</span>
              </li>
              <li className="flex items-center space-x-2 hover:text-yellow-400 transition-colors">
                <BookOpen className="w-3 h-3 text-blue-400" />
                <span>Spiritual Counseling</span>
              </li>
              <li className="flex items-center space-x-2 hover:text-yellow-400 transition-colors">
                <Award className="w-3 h-3 text-green-400" />
                <span>Life Guidance & Remedies</span>
              </li>
            </ul>
          </div>

          {/* Quick Links & Consultation Hours */}
          <div>
            <h3 className="text-xl font-semibold text-white mb-6">Quick Links</h3>
            <ul className="space-y-3 mb-8">
              <li>
                <Link to="/" className="text-purple-200 hover:text-yellow-400 transition-colors flex items-center space-x-2">
                  <span>🏠</span>
                  <span>Home</span>
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-purple-200 hover:text-yellow-400 transition-colors flex items-center space-x-2">
                  <span>ℹ️</span>
                  <span>About Pandit Ji</span>
                </Link>
              </li>
              <li>
                <Link to="/astrology-consultation" className="text-purple-200 hover:text-yellow-400 transition-colors flex items-center space-x-2">
                  <span>✨</span>
                  <span>Start Consultation</span>
                </Link>
              </li>
            </ul>

            <div className="bg-purple-900/30 p-4 rounded-lg border border-purple-400/20">
              <h4 className="text-white font-semibold mb-3 flex items-center">
                <Clock className="w-4 h-4 mr-2 text-blue-400" />
                Availability
              </h4>
              <div className="text-sm text-purple-200 space-y-1">
                <p>Chat available 24/7</p>
                <p>Consultations by appointment</p>
                <p>Worldwide service</p>
                <p className="text-yellow-300 mt-2">Start chatting now!</p>
              </div>
            </div>
          </div>
        </div>

        {/* Specializations Section */}
        <div className="border-t border-white/10 mt-12 pt-8">
          <h3 className="text-xl font-semibold text-white mb-6 text-center">Areas of Expertise</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-300/20 text-center">
              <Star className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
              <h4 className="text-white font-semibold mb-2">Vedic Astrology</h4>
              <p className="text-purple-200 text-sm">Traditional Jyotish Shastra analysis based on ancient Sanskrit texts</p>
            </div>
            <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-300/20 text-center">
              <OmLogo size={32} className="text-purple-400 mx-auto mb-3" animated={false} />
              <h4 className="text-white font-semibold mb-2">Planetary Remedies</h4>
              <p className="text-purple-200 text-sm">Effective solutions through gemstones, mantras, and spiritual practices</p>
            </div>
            <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-300/20 text-center">
              <Sun className="w-8 h-8 text-orange-400 mx-auto mb-3" />
              <h4 className="text-white font-semibold mb-2">Life Guidance</h4>
              <p className="text-purple-200 text-sm">Comprehensive guidance for career, relationships, and spiritual growth</p>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-white/10 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-center md:text-left">
              <p className="text-purple-300 text-sm">
                © 2024 Pandit Pradeep Kiradoo. All rights reserved.
              </p>
              <p className="text-purple-400 text-xs mt-1">
                Guided by ancient wisdom, powered by modern technology
              </p>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <p className="text-white text-sm font-semibold">Expert</p>
                <p className="text-purple-300 text-xs">Guidance</p>
              </div>
              <div className="text-center">
                <p className="text-white text-sm font-semibold">Vedic</p>
                <p className="text-purple-300 text-xs">Wisdom</p>
              </div>
              <div className="text-center">
                <p className="text-white text-sm font-semibold">24/7</p>
                <p className="text-purple-300 text-xs">Chat Available</p>
              </div>
            </div>
          </div>
          <div className="text-center mt-6">
            <p className="text-purple-400 text-xs italic">
              "Discover your cosmic potential and navigate life's journey with confidence through Vedic wisdom"
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
