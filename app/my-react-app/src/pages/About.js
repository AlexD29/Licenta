import React from 'react';
import './About.css';
import Footer from '../Footer';

const About = () => {
  return (
    <div>
      <div className="about-container">
        <img src="./icons/WDIVW_icon_logo.png" alt="Despre Noi" className="about-image" />
        <h1>Despre Site-ul Nostru</h1>
        <p>
          Bine ați venit pe platforma noastră inovatoare de agregare a știrilor, unde vă aducem cele mai recente articole din diverse surse, categorisindu-le după sentiment pentru a vă ajuta să rămâneți informat cu o perspectivă echilibrată. Platforma noastră culege meticulos știri de pe web, care sunt apoi analizate și categorisite în sentimente Pozitive, Negative și Neutre.
        </p>
        <p>
          Algoritmii noștri sofisticați asigură că primiți o imagine de ansamblu completă a evenimentelor curente, permițându-vă să înțelegeți perspectivele diverse care modelează lumea noastră de astăzi. Indiferent dacă sunteți interesat de politică, tehnologie, sport sau divertisment, platforma noastră oferă o agregare imparțială a știrilor pentru a vă ține la curent.
        </p>
        <p>
          Secțiunea de articole Pozitive este dedicată poveștilor înălțătoare și inspiratoare, evidențiind realizările, progresul și schimbările pozitive din diverse domenii. Secțiunea de articole Negative oferă știri critice, evidențiind provocările, conflictele și problemele care necesită atenție. Secțiunea de articole Neutre oferă rapoarte echilibrate, prezentând fapte și informații fără nicio părtinire inerentă.
        </p>
        <p>
          În plus față de categorisirea sentimentelor, generăm și statistici perspicace din datele colectate. Aceste statistici oferă o vedere de ansamblu a sentimentelor predominante în peisajul știrilor, ajutându-vă să înțelegeți starea de spirit generală și tendințele în discursul public. Vizualizările și graficele noastre fac ușor de înțeles datele complexe, oferindu-vă informații valoroase dintr-o privire.
        </p>
        <p>
          Misiunea noastră este să împuternicim cititorii cu știri complete, imparțiale și de încredere. Credem în importanța perspectivelor diverse și ne propunem să acoperim diferențele dintre diferitele puncte de vedere prin analiza sentimentelor. Alăturați-vă nouă în călătoria noastră pentru a rămâne informați, iluminați și angajați cu lumea din jurul nostru.
        </p>
        <p className="disclaimer">
          Vă rugăm să rețineți că site-ul nostru nu încearcă să fure conținut din alte surse. Scopul nostru este doar de a ajuta oamenii să obțină informații despre evenimentele curente, în special în domeniul politicii, oferind o agregare echilibrată a știrilor din diverse perspective.
        </p>
        <p>
          Vă mulțumim că ați ales platforma noastră ca sursa dvs. de încredere pentru știri. Ne angajăm să îmbunătățim continuu serviciul nostru și vă invităm să ne oferiți feedback. Rămâneți la curent pentru mai multe funcționalități și actualizări, în timp ce ne străduim să îmbunătățim experiența dvs. de citire a știrilor.
        </p>
        <div className="contact-info">
          <h2>Contactați-ne</h2>
          <p>Email: wdivw@wdivw.com</p>
          <p>Telefon: +40 757 650 548</p>
          <p>Adresă: Campusul Studențesc Codrescu, Strada Codrescu 1, Iași 700479</p>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default About;
