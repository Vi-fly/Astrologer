
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { gsap } from 'gsap';
import { Calendar, FileText, Sparkles, Star, Sun, User } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import Header from '../components/Header';
import OmLogo from '../components/OmLogo';

interface UserProfile {
  name: string;
  birthDate: string;
  birthTime: string;
  birthPlace: string;
  currentConcern: string;
  additionalInfo: string;
}

type ConsultationStage = 'form' | 'submitted';

const AstrologyConsultation = () => {
  const [userProfile, setUserProfile] = useState<UserProfile>({
    name: '',
    birthDate: '',
    birthTime: '',
    birthPlace: '',
    currentConcern: '',
    additionalInfo: ''
  });
  const [consultationStage, setConsultationStage] = useState<ConsultationStage>('form');
  const [errors, setErrors] = useState<Partial<UserProfile>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (formRef.current) {
      gsap.fromTo(formRef.current, 
        { opacity: 0, y: 50 },
        { opacity: 1, y: 0, duration: 1, ease: "power2.out" }
      );
    }
  }, []);

  const validateForm = (): boolean => {
    const newErrors: Partial<UserProfile> = {};
    
    if (!userProfile.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!userProfile.birthDate) {
      newErrors.birthDate = 'Birth date is required';
    }
    
    if (!userProfile.birthPlace.trim()) {
      newErrors.birthPlace = 'Birth place is required';
    }
    
    if (!userProfile.currentConcern.trim()) {
      newErrors.currentConcern = 'Current concern is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof UserProfile, value: string) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    // Simulate processing time
    setTimeout(() => {
      setConsultationStage('submitted');
      setIsSubmitting(false);
    }, 1500);
  };

  const resetConsultation = () => {
    setUserProfile({
      name: '',
      birthDate: '',
      birthTime: '',
      birthPlace: '',
      currentConcern: '',
      additionalInfo: ''
    });
    setConsultationStage('form');
    setErrors({});
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white relative overflow-hidden">
      <Header />
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute bg-blue-200/20 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              width: `${Math.random() * 4 + 1}px`,
              height: `${Math.random() * 4 + 1}px`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 container mx-auto px-6 py-8 pt-24 min-h-screen flex flex-col">
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-light mb-4 bg-gradient-to-r from-blue-200 via-blue-300 to-blue-400 bg-clip-text text-transparent">
            Astrological Consultation
          </h1>
          <p className="text-lg text-blue-100/80 max-w-2xl mx-auto">
            Deep analysis through planetary influences - Understanding your challenges through cosmic wisdom
          </p>
          <div className="flex items-center justify-center space-x-2 mt-4">
            <Sparkles className="w-5 h-5 text-yellow-300" />
            <span className="text-blue-200 font-medium">Consultation with Pandit Pradeep Kiradoo</span>
            <Sparkles className="w-5 h-5 text-yellow-300" />
          </div>
        </div>

        {consultationStage === 'form' && (
          <Card className="bg-blue-900/20 backdrop-blur-xl border border-blue-300/20 max-w-4xl mx-auto w-full">
            <div className="p-8">
              <form ref={formRef} onSubmit={handleSubmit} className="space-y-8">
                {/* Personal Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-blue-200 flex items-center space-x-2">
                    <User className="w-5 h-5" />
                    <span>Personal Information</span>
                  </h3>
                  
                  <div>
                    <Label htmlFor="name" className="text-blue-100">Full Name *</Label>
                    <Input
                      id="name"
                      type="text"
                      value={userProfile.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className={`bg-blue-800/20 border-blue-300/30 text-blue-100 placeholder-blue-200/60 focus:border-blue-400 focus:ring-blue-400/30 ${errors.name ? 'border-red-400' : ''}`}
                      placeholder="Enter your full name"
                      required
                    />
                    {errors.name && <p className="text-red-400 text-sm mt-1">{errors.name}</p>}
                  </div>
                </div>

                {/* Birth Details */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-blue-200 flex items-center space-x-2">
                    <Calendar className="w-5 h-5" />
                    <span>Birth Details</span>
                  </h3>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="birthDate" className="text-blue-100">Date of Birth *</Label>
                      <Input
                        id="birthDate"
                        type="date"
                        value={userProfile.birthDate}
                        onChange={(e) => handleInputChange('birthDate', e.target.value)}
                        className={`bg-blue-800/20 border-blue-300/30 text-blue-100 focus:border-blue-400 focus:ring-blue-400/30 ${errors.birthDate ? 'border-red-400' : ''}`}
                        required
                      />
                      {errors.birthDate && <p className="text-red-400 text-sm mt-1">{errors.birthDate}</p>}
                    </div>
                    
                    <div>
                      <Label htmlFor="birthTime" className="text-blue-100">Time of Birth</Label>
                      <Input
                        id="birthTime"
                        type="time"
                        value={userProfile.birthTime}
                        onChange={(e) => handleInputChange('birthTime', e.target.value)}
                        className="bg-blue-800/20 border-blue-300/30 text-blue-100 focus:border-blue-400 focus:ring-blue-400/30"
                        placeholder="If known"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="birthPlace" className="text-blue-100">Place of Birth *</Label>
                    <Input
                      id="birthPlace"
                      type="text"
                      value={userProfile.birthPlace}
                      onChange={(e) => handleInputChange('birthPlace', e.target.value)}
                      className={`bg-blue-800/20 border-blue-300/30 text-blue-100 placeholder-blue-200/60 focus:border-blue-400 focus:ring-blue-400/30 ${errors.birthPlace ? 'border-red-400' : ''}`}
                      placeholder="City, State, Country"
                      required
                    />
                    {errors.birthPlace && <p className="text-red-400 text-sm mt-1">{errors.birthPlace}</p>}
                  </div>
                </div>

                {/* Current Concerns */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-blue-200 flex items-center space-x-2">
                    <FileText className="w-5 h-5" />
                    <span>Current Concerns</span>
                  </h3>
                  
                  <div>
                    <Label htmlFor="currentConcern" className="text-blue-100">Primary Concern *</Label>
                    <Textarea
                      id="currentConcern"
                      value={userProfile.currentConcern}
                      onChange={(e) => handleInputChange('currentConcern', e.target.value)}
                      className={`bg-blue-800/20 border-blue-300/30 text-blue-100 placeholder-blue-200/60 focus:border-blue-400 focus:ring-blue-400/30 min-h-[100px] ${errors.currentConcern ? 'border-red-400' : ''}`}
                      placeholder="Describe your main concern or challenge in detail..."
                      required
                    />
                    {errors.currentConcern && <p className="text-red-400 text-sm mt-1">{errors.currentConcern}</p>}
                  </div>
                  
                  <div>
                    <Label htmlFor="additionalInfo" className="text-blue-100">Additional Information</Label>
                    <Textarea
                      id="additionalInfo"
                      value={userProfile.additionalInfo}
                      onChange={(e) => handleInputChange('additionalInfo', e.target.value)}
                      className="bg-blue-800/20 border-blue-300/30 text-blue-100 placeholder-blue-200/60 focus:border-blue-400 focus:ring-blue-400/30 min-h-[80px]"
                      placeholder="Any additional context, background, or specific questions..."
                    />
                  </div>
                </div>

                <Button 
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-blue-500/80 hover:bg-blue-600/90 text-white py-3 text-lg border-0 hover:scale-105 transition-all duration-300 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-center space-x-2">
                    {isSubmitting ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Submitting...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5" />
                        <span>Submit Consultation Request</span>
                      </>
                    )}
                  </div>
                </Button>
              </form>
            </div>
          </Card>
        )}

        {consultationStage === 'submitted' && (
          <Card className="bg-blue-900/20 backdrop-blur-xl border border-blue-300/20 max-w-2xl mx-auto w-full">
            <div className="p-12 text-center">
              <div className="flex items-center justify-center space-x-3 mb-6">
                <Star className="w-8 h-8 text-yellow-300 animate-pulse" />
                <OmLogo size={32} className="text-blue-300" />
                <Sun className="w-8 h-8 text-orange-300 animate-pulse" />
              </div>
              <h2 className="text-2xl font-semibold text-blue-200 mb-4">
                Consultation Request Submitted
              </h2>
              <p className="text-blue-100/80 mb-6">
                Thank you for submitting your consultation request, {userProfile.name}! 
                Pandit Pradeep Kiradoo will review your information and provide you with a comprehensive astrological analysis.
              </p>
              <p className="text-blue-100/70 text-sm mb-8">
                Your consultation details have been recorded. You will receive your personalized astrological report soon.
              </p>
              
              <div className="bg-blue-800/20 p-6 rounded-lg border border-blue-300/20 mb-8">
                <h3 className="text-lg font-medium text-blue-200 mb-4">Consultation Summary</h3>
                <div className="text-left space-y-2 text-sm text-blue-100/80">
                  <p><strong>Name:</strong> {userProfile.name}</p>
                  <p><strong>Birth Date:</strong> {userProfile.birthDate}</p>
                  {userProfile.birthTime && <p><strong>Birth Time:</strong> {userProfile.birthTime}</p>}
                  <p><strong>Birth Place:</strong> {userProfile.birthPlace}</p>
                  <p><strong>Primary Concern:</strong> {userProfile.currentConcern}</p>
                  {userProfile.additionalInfo && <p><strong>Additional Info:</strong> {userProfile.additionalInfo}</p>}
                </div>
          </div>

              <Button 
                onClick={resetConsultation}
                className="bg-blue-500/80 hover:bg-blue-600/90 text-white px-8 py-3 border-0 hover:scale-105 transition-all duration-300 hover:shadow-lg"
              >
                Submit Another Consultation
              </Button>
          </div>
        </Card>
        )}
      </div>
    </div>
  );
};

export default AstrologyConsultation;
