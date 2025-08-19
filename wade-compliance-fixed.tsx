import React from 'react';

export default function Home() {
  const [images, setImages] = React.useState({});

  React.useEffect(() => {
    const loadImages = async () => {
      const imageMap = {};
      for (let i = 1; i <= 7; i++) {
        try {
          const data = await window.fs.readFile(`Image ${i}`);
          const blob = new Blob([data], { type: 'image/jpeg' });
          imageMap[`image${i}`] = URL.createObjectURL(blob);
        } catch (error) {
          console.error(`Error loading Image ${i}:`, error);
        }
      }
      setImages(imageMap);
    };
    loadImages();
  }, []);

  return (
    <div style={{ 
      fontFamily: '"League Spartan", system-ui, -apple-system, sans-serif',
      lineHeight: 1.6,
      color: '#1a1a1a'
    }}>
      {/* Navigation */}
      <nav style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        background: 'rgba(0, 51, 102, 0.95)',
        backdropFilter: 'blur(10px)',
        zIndex: 1000,
        padding: '12px 0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {images.image2 && (
              <img src={images.image2} alt="Wade Compliance Solutions" style={{ width: '32px', height: '32px', objectFit: 'cover' }} />
            )}
            <span style={{ color: 'white', fontSize: '18px', fontWeight: 600 }}>Wade Compliance Solutions</span>
          </div>
          <div style={{ display: 'flex', gap: '32px' }}>
            <a href="#services" style={{ color: 'white', textDecoration: 'none', fontWeight: 500, fontSize: '14px' }}>Services</a>
            <a href="#about" style={{ color: 'white', textDecoration: 'none', fontWeight: 500, fontSize: '14px' }}>About</a>
            <a href="#contact" style={{ color: 'white', textDecoration: 'none', fontWeight: 500, fontSize: '14px' }}>Contact</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        minHeight: '100vh',
        background: images.image1 ? `linear-gradient(rgba(0, 51, 102, 0.8), rgba(0, 51, 102, 0.6)), url(${images.image1})` : 'linear-gradient(135deg, #003366 0%, #1a4b73 100%)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        display: 'flex',
        alignItems: 'center',
        color: 'white',
        position: 'relative'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', width: '100%' }}>
          <div style={{ maxWidth: '700px' }}>
            <h1 style={{ 
              fontSize: 'clamp(3rem, 8vw, 5rem)', 
              fontWeight: 800, 
              marginBottom: '24px', 
              lineHeight: 1.1,
              letterSpacing: '-0.02em'
            }}>
              Compliance.<br />
              <span style={{ color: '#4a90e2' }}>Simplified.</span>
            </h1>
            <p style={{ 
              fontSize: '22px', 
              marginBottom: '40px', 
              opacity: 0.9,
              fontWeight: 300,
              lineHeight: 1.4
            }}>
              Turnkey compliance solutions for government and enterprise clients. 
              We bridge regulatory requirements with operational excellence.
            </p>
            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
              <button style={{
                background: '#4a90e2',
                color: 'white',
                border: 'none',
                padding: '16px 32px',
                fontSize: '16px',
                fontWeight: 600,
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}>
                Schedule Consultation
              </button>
              <button style={{
                background: 'transparent',
                color: 'white',
                border: '2px solid white',
                padding: '14px 32px',
                fontSize: '16px',
                fontWeight: 600,
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}>
                View Services
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section style={{ 
        background: '#f8fafc', 
        padding: '80px 0',
        borderBottom: '1px solid #e2e8f0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px', textAlign: 'center' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#64748b', marginBottom: '32px', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Certified & Trusted
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '40px' }}>
            <div>
              <div style={{ fontSize: '32px', fontWeight: 800, color: '#003366', marginBottom: '8px' }}>MBE</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>Minority Business Enterprise</div>
            </div>
            <div>
              <div style={{ fontSize: '32px', fontWeight: 800, color: '#003366', marginBottom: '8px' }}>SB(Micro)</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>California Certified</div>
            </div>
            <div>
              <div style={{ fontSize: '32px', fontWeight: 800, color: '#003366', marginBottom: '8px' }}>HUBZone</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>Federal Designation</div>
            </div>
            <div>
              <div style={{ fontSize: '32px', fontWeight: 800, color: '#003366', marginBottom: '8px' }}>NIST</div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>Framework Expertise</div>
            </div>
          </div>
        </div>
      </section>

      {/* Value Propositions */}
      <section id="about" style={{ padding: '120px 0', background: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h2 style={{ 
              fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', 
              fontWeight: 800, 
              color: '#003366', 
              marginBottom: '24px',
              lineHeight: 1.1
            }}>
              The Compliance Advantage
            </h2>
            <p style={{ fontSize: '20px', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>
              Four key benefits that set your organization apart in competitive bidding and regulatory environments.
            </p>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '40px' }}>
            <div style={{ 
              background: '#f8fafc', 
              padding: '40px', 
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              transition: 'all 0.3s ease'
            }}>
              <div style={{ 
                width: '60px', 
                height: '60px', 
                background: '#4a90e2', 
                borderRadius: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                marginBottom: '24px'
              }}>
                <span style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>🎯</span>
              </div>
              <h3 style={{ fontSize: '22px', fontWeight: 700, color: '#003366', marginBottom: '16px' }}>
                Bid-Ready Advantage
              </h3>
              <p style={{ color: '#64748b', lineHeight: 1.6 }}>
                Avoid disqualification and gain competitive edge through proactive compliance gap identification and correction before award.
              </p>
            </div>

            <div style={{ 
              background: '#f8fafc', 
              padding: '40px', 
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              transition: 'all 0.3s ease'
            }}>
              <div style={{ 
                width: '60px', 
                height: '60px', 
                background: '#4a90e2', 
                borderRadius: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                marginBottom: '24px'
              }}>
                <span style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>🛡️</span>
              </div>
              <h3 style={{ fontSize: '22px', fontWeight: 700, color: '#003366', marginBottom: '16px' }}>
                Risk Reduction
              </h3>
              <p style={{ color: '#64748b', lineHeight: 1.6 }}>
                Lower exposure to fines, penalties, and reputational harm through comprehensive, proactive compliance management.
              </p>
            </div>

            <div style={{ 
              background: '#f8fafc', 
              padding: '40px', 
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              transition: 'all 0.3s ease'
            }}>
              <div style={{ 
                width: '60px', 
                height: '60px', 
                background: '#4a90e2', 
                borderRadius: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                marginBottom: '24px'
              }}>
                <span style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>🤝</span>
              </div>
              <h3 style={{ fontSize: '22px', fontWeight: 700, color: '#003366', marginBottom: '16px' }}>
                Supplier Diversity Leverage
              </h3>
              <p style={{ color: '#64748b', lineHeight: 1.6 }}>
                Our MBE, SB(Micro), and HUBZone certifications provide valuable supplier diversity credits for prime contractors.
              </p>
            </div>

            <div style={{ 
              background: '#f8fafc', 
              padding: '40px', 
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              transition: 'all 0.3s ease'
            }}>
              <div style={{ 
                width: '60px', 
                height: '60px', 
                background: '#4a90e2', 
                borderRadius: '12px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                marginBottom: '24px'
              }}>
                <span style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>⚡</span>
              </div>
              <h3 style={{ fontSize: '22px', fontWeight: 700, color: '#003366', marginBottom: '16px' }}>
                Speed & Flexibility
              </h3>
              <p style={{ color: '#64748b', lineHeight: 1.6 }}>
                Rapid deployment and execution of compliance reviews without the overhead of larger consultancies.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" style={{ 
        padding: '120px 0',
        background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h2 style={{ 
              fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', 
              fontWeight: 800, 
              color: '#003366', 
              marginBottom: '24px' 
            }}>
              Comprehensive Compliance Services
            </h2>
            <p style={{ fontSize: '20px', color: '#64748b', maxWidth: '700px', margin: '0 auto' }}>
              From IT security frameworks to government contracting requirements, we provide end-to-end compliance solutions.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '32px' }}>
            {[
              {
                title: "IT & Cybersecurity Compliance",
                description: "NIST frameworks, SOC 2, ISO 27001, CMMC readiness assessments and implementation support.",
                image: images.image3
              },
              {
                title: "Government Contract Compliance",
                description: "Procurement audits, bid compliance reviews, subcontractor tracking, and regulatory reporting.",
                image: images.image4
              },
              {
                title: "ADA & Accessibility Audits",
                description: "Comprehensive accessibility assessments ensuring compliance with federal and state requirements.",
                image: images.image5
              },
              {
                title: "Environmental & Safety Reviews",
                description: "Environmental regulation compliance, fire safety assessments, and workplace safety audits.",
                image: images.image6
              }
            ].map((service, index) => (
              <div key={index} style={{
                background: 'white',
                borderRadius: '16px',
                overflow: 'hidden',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.3s ease'
              }}>
                {service.image && (
                  <div style={{ 
                    height: '200px', 
                    background: `url(${service.image})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center'
                  }} />
                )}
                <div style={{ padding: '32px' }}>
                  <h3 style={{ 
                    fontSize: '22px', 
                    fontWeight: 700, 
                    color: '#003366', 
                    marginBottom: '16px',
                    lineHeight: 1.2
                  }}>
                    {service.title}
                  </h3>
                  <p style={{ color: '#64748b', lineHeight: 1.6, marginBottom: '24px' }}>
                    {service.description}
                  </p>
                  <button style={{
                    color: '#4a90e2',
                    background: 'transparent',
                    border: 'none',
                    fontSize: '16px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    padding: '8px 0'
                  }}>
                    Learn More →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section style={{ padding: '120px 0', background: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h2 style={{ 
              fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', 
              fontWeight: 800, 
              color: '#003366', 
              marginBottom: '24px' 
            }}>
              Leadership Team
            </h2>
            <p style={{ fontSize: '20px', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>
              Experienced professionals with deep expertise in compliance, security, and government contracting.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '40px', marginBottom: '60px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{
                width: '120px',
                height: '120px',
                background: 'linear-gradient(135deg, #4a90e2, #003366)',
                borderRadius: '50%',
                margin: '0 auto 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{ color: 'white', fontSize: '48px', fontWeight: 'bold' }}>D</span>
              </div>
              <h3 style={{ fontSize: '24px', fontWeight: 700, color: '#003366', marginBottom: '8px' }}>
                CEO & Founder
              </h3>
              <p style={{ color: '#64748b', marginBottom: '16px' }}>
                Compliance vision and minority-owned business leadership with extensive certification experience.
              </p>
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{
                width: '120px',
                height: '120px',
                background: 'linear-gradient(135deg, #4a90e2, #003366)',
                borderRadius: '50%',
                margin: '0 auto 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{ color: 'white', fontSize: '48px', fontWeight: 'bold' }}>B</span>
              </div>
              <h3 style={{ fontSize: '24px', fontWeight: 700, color: '#003366', marginBottom: '8px' }}>
                Business Manager
              </h3>
              <p style={{ color: '#64748b', marginBottom: '16px' }}>
                Enterprise compliance strategy, client engagement, and government contracting expertise.
              </p>
            </div>
          </div>

          <div style={{ 
            background: '#f8fafc', 
            padding: '40px', 
            borderRadius: '16px', 
            textAlign: 'center',
            border: '1px solid #e2e8f0'
          }}>
            <h4 style={{ fontSize: '20px', fontWeight: 700, color: '#003366', marginBottom: '16px' }}>
              Advisory Network
            </h4>
            <p style={{ color: '#64748b', fontSize: '16px' }}>
              Supported by cybersecurity, procurement, and legal experts to ensure comprehensive compliance coverage.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" style={{
        padding: '120px 0',
        background: images.image7 ? `linear-gradient(rgba(0, 51, 102, 0.9), rgba(0, 51, 102, 0.8)), url(${images.image7})` : 'linear-gradient(135deg, #003366 0%, #1a4b73 100%)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        color: 'white'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '60px', alignItems: 'center' }}>
            <div>
              <h2 style={{ 
                fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', 
                fontWeight: 800, 
                marginBottom: '24px' 
              }}>
                Ready to Get Compliant?
              </h2>
              <p style={{ fontSize: '20px', marginBottom: '32px', opacity: 0.9 }}>
                Trusted by agencies and contractors across California. 
                Let's discuss how we can streamline your compliance requirements.
              </p>
              
              <div style={{ marginBottom: '32px' }}>
                <div style={{ marginBottom: '16px' }}>
                  <span style={{ fontWeight: 600 }}>Email:</span>
                  <a href="mailto:donta@wadecompliance.com" style={{ color: '#4a90e2', textDecoration: 'none', marginLeft: '8px' }}>
                    donta@wadecompliance.com
                  </a>
                </div>
                <div style={{ marginBottom: '16px' }}>
                  <span style={{ fontWeight: 600 }}>Phone:</span>
                  <a href="tel:+18185739736" style={{ color: '#4a90e2', textDecoration: 'none', marginLeft: '8px' }}>
                    (818) 573-9736
                  </a>
                </div>
                <div>
                  <span style={{ fontWeight: 600 }}>Website:</span>
                  <a href="https://wadecompliance.com" target="_blank" rel="noopener noreferrer" style={{ color: '#4a90e2', textDecoration: 'none', marginLeft: '8px' }}>
                    wadecompliance.com
                  </a>
                </div>
              </div>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              padding: '40px',
              borderRadius: '16px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <h3 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '24px' }}>
                Schedule Consultation
              </h3>
              <form style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <input
                  type="text"
                  placeholder="Full Name"
                  style={{
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    fontSize: '16px'
                  }}
                />
                <input
                  type="email"
                  placeholder="Email Address"
                  style={{
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    fontSize: '16px'
                  }}
                />
                <textarea
                  placeholder="Describe your compliance needs..."
                  rows={4}
                  style={{
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    fontSize: '16px',
                    resize: 'vertical'
                  }}
                />
                <button style={{
                  background: '#4a90e2',
                  color: 'white',
                  border: 'none',
                  padding: '16px',
                  fontSize: '16px',
                  fontWeight: 600,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}>
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ 
        background: '#0a0a0a', 
        color: 'white', 
        padding: '60px 0 40px',
        textAlign: 'center'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', marginBottom: '32px' }}>
            {images.image2 && (
              <img src={images.image2} alt="Wade Compliance Solutions" style={{ width: '40px', height: '40px', objectFit: 'cover' }} />
            )}
            <span style={{ fontSize: '20px', fontWeight: 700 }}>Wade Compliance Solutions</span>
          </div>
          
          <div style={{ 
            borderTop: '1px solid #333', 
            paddingTop: '32px', 
            fontSize: '14px', 
            opacity: 0.7 
          }}>
            © {new Date().getFullYear()} Wade Compliance Solutions LLC. All rights reserved. | MBE Certified | SB(Micro) Certified | HUBZone Designated
          </div>
        </div>
      </footer>
    </div>
  );
}