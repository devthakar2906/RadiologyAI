# RADIOLOGY AI PLATFORM

## Copy-Paste Master Report Source

This file is prepared as a clean content source for your final GTU project report. The section order follows the sample file `Clg/Report_sample.pdf`, and the writing has been kept simple, formal, and student-like so it does not read like polished marketing or AI-generated copy.

Use this file only as the content base. In Word, format it exactly as shown in the sample PDF.

Strict order to maintain:

1. Cover Page
2. First Page
3. College Certificate
4. Company Certificate
5. Candidate Declaration
6. Acknowledgement
7. Abstract
8. List of Figures
9. List of Tables
10. List of Abbreviations
11. Table of Contents
12. Chapters
13. Appendix
14. References

---

# COVER PAGE

**RADIOLOGY AI PLATFORM**

A  
**PROJECT REPORT**

Submitted by  
**DEV THAKAR**  
**230673107042**

In partial fulfillment for the award of the degree of  
**BACHELOR OF ENGINEERING**

in  
**COMPUTER ENGINEERING**

**SAL INSTITUTE OF TECHNOLOGY AND ENGINEERING RESEARCH**  
App. Science City, Sola Road, Ahmedabad, 380060

Gujarat Technological University, Ahmedabad  
**April 2026**

---

# FIRST PAGE

**RADIOLOGY AI PLATFORM**

A  
**PROJECT REPORT**

Submitted by  
**DEV THAKAR**  
**230673107042**

In partial fulfillment for the award of the degree of  
**BACHELOR OF ENGINEERING**

in  
**COMPUTER ENGINEERING**

**SAL INSTITUTE OF TECHNOLOGY AND ENGINEERING RESEARCH**  
App. Science City, Sola Road, Ahmedabad, 380060

Gujarat Technological University, Ahmedabad  
**Academic Year: 2025-26**

---

# COLLEGE CERTIFICATE

**SAL INSTITUTE OF TECHNOLOGY AND ENGINEERING RESEARCH**  
App. Science City, Sola Road, Ahmedabad, 380060

## CERTIFICATE

This is to certify that the project report submitted along with the project entitled **"Radiology AI Platform"** has been carried out by **Dev Thakar** under my guidance in partial fulfillment for the degree of **Bachelor of Engineering in Computer Engineering**, 8th Semester of **Gujarat Technological University, Ahmedabad** during the academic year **2025-26**.

**Komal Thummar**  
Internal Guide

**Dr. Nimisha Patel**  
Head of the Department

---

# COMPANY CERTIFICATE

**FICE Education Pvt. Ltd.**  
Remote Internship

**Date:** 01/04/2026

## TO WHOM IT MAY CONCERN

This is to certify that **Dev Thakar**, a student of **Sal Institute of Technology and Engineering Research**, has successfully completed his internship in the field of **Full Stack Software Development and AI-Based Reporting Systems** from **21/01/2026** to **01/04/2026** (Total number of Weeks: **12**) under the guidance of **Ms. Anjali Singh**.

During the internship period, he worked on the development of the **Radiology AI Platform**. His work included studying the reporting workflow, designing backend APIs, developing frontend screens, integrating AI-assisted transcription refinement, generating structured reports, handling encrypted data storage, and testing different modules of the system.

During the period of his internship program with us, he was sincere in his work, willing to learn, and regular in completing the assigned tasks.

We wish him success in his future academic and professional career.

For **FICE Education Pvt. Ltd.**

**Anjali Singh**  
Industry Mentor

---

# CANDIDATE DECLARATION

**SAL INSTITUTE OF TECHNOLOGY AND ENGINEERING RESEARCH**  
Opp. Science City, Sola Road, Ahmedabad, 380060

## DECLARATION

I hereby declare that the Internship / Project report submitted along with the Internship / Project entitled **"Radiology AI Platform"** submitted in partial fulfillment for the degree of **Bachelor of Engineering in Computer Engineering** to **Gujarat Technological University, Ahmedabad**, is a bonafide record of original project work carried out by me at **FICE Education Pvt. Ltd.** under the supervision of **Ms. Anjali Singh** and **Ms. Komal Thummar**, and that no part of this report has been directly copied from any students' reports or taken from any other source without giving proper reference.

**Name of Student:** Dev Thakar  
**Sign of Student:** ____________________

---

# ACKNOWLEDGEMENT

I would like to express my sincere thanks to everyone who supported me during the development of this project.

First of all, I am thankful to my internal guide, **Ms. Komal Thummar**, for her guidance, valuable suggestions, and constant encouragement throughout the project work. Her academic support helped me stay focused and complete the project in a proper manner.

I am also thankful to **Dr. Nimisha Patel**, Head of the Department of Computer Engineering, for providing the necessary facilities and academic environment required for this work.

I would also like to thank my industry mentor, **Ms. Anjali Singh**, and **FICE Education Pvt. Ltd.** for giving me the opportunity to work on a practical project during my internship. Through this work, I was able to learn how real software systems are planned, developed, tested, and improved.

I am grateful to all faculty members of the department for their support and motivation. Finally, I would like to thank my family and friends for their encouragement and support throughout the project period.

**Dev Thakar**  
**230673107042**

---

# ABSTRACT

Radiology reporting is an important part of medical workflow. In many cases, doctors first speak or type their findings and then manually convert them into a proper report. This process takes time and can lead to inconsistency in formatting and content structure. The project **"Radiology AI Platform"** was developed to make this process easier by helping convert findings into structured reports in a more efficient way.

The proposed system is a full-stack web application developed using **FastAPI**, **React**, **PostgreSQL**, **Redis**, and **Celery**. It supports login for doctor and admin users, live dictation through the browser, audio upload, transcript refinement using AI APIs, structured report generation from findings, encrypted storage of reports, report search, and PDF export.

The main aim of the project is to reduce repetitive manual work in report preparation and provide a cleaner and more organized reporting workflow. Instead of running large AI models locally, the project uses API-based services, which keeps the system lightweight and practical.

The final outcome of the project is a working platform that combines modern web development with AI-assisted reporting support. It is useful as both an academic project and a practical implementation in the field of structured medical documentation.

---

# LIST OF FIGURES

1. Fig 1.1 Overview of company and project environment  
2. Fig 2.1 Internship work flow  
3. Fig 3.1 High-level workflow of Radiology AI Platform  
4. Fig 4.1 Authentication and access flow  
5. Fig 4.2 Audio transcription and refinement flow  
6. Fig 4.3 Structured report generation flow  
7. Fig 4.4 Background processing using Celery and Redis  
8. Fig 5.1 Landing page  
9. Fig 5.2 Report dashboard  
10. Fig 5.3 Structured report editor and PDF export  
11. Fig 6.1 Sample output of generated report  

---

# LIST OF TABLES

1. Table 1.1 Internship and company overview  
2. Table 2.1 Technical exposure during internship  
3. Table 3.1 Objectives of the project  
4. Table 3.2 Technology stack used  
5. Table 4.1 Main modules of the system  
6. Table 4.2 Database entities  
7. Table 5.1 Implementation modules  
8. Table 6.1 Testing results  

---

# LIST OF ABBREVIATIONS

- **AI** - Artificial Intelligence  
- **API** - Application Programming Interface  
- **ASR** - Automatic Speech Recognition  
- **AES** - Advanced Encryption Standard  
- **DB** - Database  
- **JWT** - JSON Web Token  
- **LLM** - Large Language Model  
- **PDF** - Portable Document Format  
- **UI** - User Interface  
- **UX** - User Experience  
- **SQL** - Structured Query Language  
- **PACS** - Picture Archiving and Communication System  
- **STT** - Speech to Text  

---

# TABLE OF CONTENTS

Maintain the following order in Word:

- Acknowledgement  
- Abstract  
- List of Figures  
- List of Tables  
- List of Abbreviations  
- Table of Contents  
- Chapter 1 Overview of the Company  
- Chapter 2 Overview of Different Department / Work Environment  
- Chapter 3 Introduction to Project / Internship and Project Management  
- Chapter 4 System Analysis  
- Chapter 5 System Design  
- Chapter 6 Implementation  
- Chapter 7 Testing  
- Chapter 8 Conclusion and Discussion  
- References  
- Appendix  

---

# CHAPTER 1 OVERVIEW OF THE COMPANY

## 1.1 History

**FICE Education Pvt. Ltd.** is an organization involved in technical training, educational support, and practical software project development. The company provides students and interns with opportunities to work on real implementation tasks so that they can understand how academic knowledge is used in actual development work.

During the internship period, the company provided a proper environment for learning modern tools and development practices. The project assigned to me was not only useful from a learning point of view but also relevant to current software and AI-based application trends.

## 1.2 Different Product / Scope of Work

The company works in areas related to technical education, project support, and digital solution development. As part of my internship, I was assigned the responsibility of working on an AI-assisted radiology reporting system.

The scope of the work included:

- understanding the reporting process,
- planning the application flow,
- developing backend APIs,
- creating the frontend dashboard,
- connecting AI-based transcript refinement,
- generating structured reports,
- storing reports securely,
- and providing search and export functionality.

## 1.3 Organization Chart

The work structure followed during the internship can be represented as:

- Company / Management  
- Industry Mentor  
- Project Guidance and Review  
- Student Intern / Developer  

In this project, **Ms. Anjali Singh** guided the work from the industry side.

## 1.4 Capacity of Work Environment

The internship was carried out in remote mode. Even though it was remote, the work environment remained structured. Guidance was provided whenever needed, and the project work was performed through continuous learning, implementation, review, and correction.

The remote nature of the internship also helped in developing self-planning, regular progress tracking, and discipline in handling technical tasks independently.

---

# CHAPTER 2 OVERVIEW OF DIFFERENT DEPARTMENT / WORK ENVIRONMENT

## 2.1 Details About the Work Carried Out

The work carried out during the internship can be divided into the following major technical parts.

### 2.1.1 Requirement Understanding and Domain Study

At the beginning, I studied how radiology findings are usually written and how raw spoken findings can be converted into organized report sections. This step helped in understanding the practical problem that the project was trying to solve.

### 2.1.2 Backend Development

The backend part of the project was developed using **FastAPI**. The work included creating routes, authentication logic, role handling, database connection, report save and retrieval flow, background task support, and integration with external AI APIs.

### 2.1.3 Frontend Development

The frontend was developed using **React**, **Vite**, and **Tailwind CSS**. This part included creating the homepage, login and signup screens, report dashboard, speech input section, editable report panel, search interface, and PDF download options.

### 2.1.4 AI Integration

The project integrates AI support through **Hugging Face APIs**. The main use of AI in the project is for transcript refinement and structured report generation. The objective was to keep the system lightweight and avoid local heavy model loading.

### 2.1.5 Testing and Refinement

The completed features were tested repeatedly for login, report creation, audio handling, report saving, keyword search, admin filtering, PDF generation, and concurrent task flow.

## 2.2 Technical Specifications of Major Tools Used

- **Backend Framework:** FastAPI  
- **Frontend Framework:** React  
- **Database:** PostgreSQL  
- **Queue / Broker:** Redis  
- **Background Processing:** Celery  
- **Monitoring:** Flower  
- **Styling:** Tailwind CSS  
- **Editor:** Quill  
- **AI Services:** Hugging Face Inference APIs  
- **Migration:** Alembic  
- **Authentication:** JWT and cookie-based flow  
- **Encryption:** AES-based storage encryption  

## 2.3 Sequence of Operation for the Project

The basic sequence followed in the system is:

1. User logs into the platform.  
2. Findings are entered by typing, live speech, or audio upload.  
3. Audio is sent for refinement.  
4. Findings are converted into structured report output.  
5. User reviews and edits the report.  
6. Report is saved, searched, or exported.  
7. Heavy tasks run in the background.  

## 2.4 Explanation of Each Stage

Each stage of the system has a clear purpose. The input stage collects user findings. The refinement stage improves raw text. The generation stage organizes the content into sections. The storage stage saves the report securely. The retrieval stage helps in search and reuse. The export stage gives a final usable document.

---

# CHAPTER 3 INTRODUCTION TO PROJECT / INTERNSHIP AND PROJECT MANAGEMENT

## 3.1 Project Summary

The **Radiology AI Platform** is a web-based reporting system developed to help convert radiology findings into structured reports. The system supports doctor and admin login, live dictation, uploaded audio refinement, report generation from findings, encrypted storage, search, and PDF export.

The main idea behind the project is to reduce manual effort in report preparation and improve consistency in the final output.

## 3.2 Purpose

The purpose of the project is to build a platform that makes report preparation easier and more organized. Instead of writing every report manually in free form, the system helps turn findings into a structured result that can be reviewed and saved.

## 3.3 Objective

The objectives of the project are:

- to capture findings easily,
- to refine transcription,
- to generate structured reports,
- to store reports securely,
- to support search and retrieval,
- to provide editable output,
- and to handle multiple requests efficiently.

## 3.4 Scope

The project covers:

- live dictation,
- typed findings,
- uploaded audio,
- structured report generation,
- encrypted report storage,
- history and search,
- admin filtering,
- and PDF export.

The system is meant to assist report preparation, not replace medical expertise.

## 3.5 Technology and Literature Review

The project uses FastAPI for backend APIs, PostgreSQL for data storage, Redis and Celery for asynchronous processing, React and Tailwind for frontend, and Hugging Face APIs for AI support. From the study of available tools and systems, it was understood that combining structured templates with lightweight API-based AI is a practical approach for this type of application.

## 3.6 Project / Internship Planning

The project was planned in stages such as:

- understanding the problem,
- setting up the development environment,
- building backend modules,
- building frontend pages,
- integrating AI and structured generation,
- adding storage and search,
- and testing the overall flow.

### 3.6.1 Development Approach and Justification

An iterative approach was used because the project contained multiple connected modules. This made it easier to build one feature at a time, test it, and improve it before moving to the next stage.

### 3.6.2 Effort and Time Estimation

The work was completed during the 12-week internship period. Time was divided between planning, development, debugging, integration, and documentation.

### 3.6.3 Roles and Responsibilities

- **Student:** development, testing, integration, documentation  
- **Industry Mentor:** review and technical guidance  
- **Internal Guide:** academic guidance and supervision  

### 3.6.4 Group Dependencies

This was an individual project, so there were no group dependencies.

## 3.7 Project Scheduling

The project progress broadly followed this schedule:

- Weeks 1-2: study and planning  
- Weeks 3-4: backend and database setup  
- Weeks 5-6: frontend implementation  
- Weeks 7-8: AI and reporting workflow  
- Weeks 9-10: save, search, and export features  
- Weeks 11-12: testing and documentation  

---

# 
---

# CHAPTER 5 SYSTEM DESIGN

## 5.1 System Design and Methodology

The system is designed in modular layers. The frontend handles interaction and report editing. The backend manages APIs and business logic. The database stores user and report data. Redis and Celery manage background tasks. AI services are used through APIs for refinement and structured generation.

## 5.2 Database Design / Data Structure Design

The main database entities are:

### User

- id  
- name  
- email  
- password  
- role  

### Report

- id  
- user_id  
- transcription  
- report  
- audio_hash  
- audio_path  
- created_at  

### Log

- id  
- user_id  
- action  
- status  
- timestamp  

The report and transcription are stored in encrypted form.

## 5.3 Input / Output and Interface Design

### 5.3.1 Input Design

The system accepts:

- typed findings,
- live dictated findings,
- uploaded audio.

### 5.3.2 Output Design

The system produces:

- refined transcription,
- structured report sections,
- saved report history,
- downloadable PDF output.

### 5.3.3 Access Control / Security

The security design includes doctor and admin roles, protected APIs, encryption of report data, and request limiting for sensitive routes.

---

# CHAPTER 6 IMPLEMENTATION

## 6.1 Implementation Platform / Environment

The development environment included Python for backend implementation, React for frontend implementation, PostgreSQL for the database, Redis for queue support, Celery workers for background processing, and external AI APIs for refinement and structured output.

## 6.2 Process / Program / Technology / Modules Specification

### Backend Modules

- authentication routes  
- report APIs  
- dependency and security handlers  
- AI services  
- template services  
- formatter services  
- Redis utilities  
- Celery tasks  
- migration support  

### Frontend Modules

- landing homepage  
- login and signup pages  
- report dashboard  
- speech input UI  
- editable report viewer  
- report history panel  
- theme support  
- PDF export utility  

## 6.3 Findings / Results / Outcomes

The final system provides:

- working authentication,
- report generation from findings,
- audio refinement support,
- secure storage,
- report history,
- search and filters,
- and PDF export.

## 6.4 Result Analysis / Comparison / Deliberations

Compared to manual documentation, the developed platform reduces repeated formatting work and makes reports easier to manage. It also provides better structure and faster retrieval. Most importantly, the project shows that a useful AI-assisted reporting workflow can be built without depending on heavy local hardware.

---

# CHAPTER 7 TESTING

## 7.1 Testing Plan / Strategy

Testing was carried out for each module as well as for the full flow. The main testing areas were login, role handling, transcription flow, report generation, save flow, search, export, and background processing.

## 7.2 Test Results and Analysis

The project was tested under normal user actions and the expected outputs were received in the major flows. Login and signup worked correctly. Findings were converted into structured reports. Saved reports appeared in history. Search and export worked as intended.

### 7.2.1 Test Cases

Suggested test table in Word:

- Test ID  
- Test Condition  
- Expected Output  
- Actual Output  
- Remark  

Example cases:

1. Valid doctor login  
2. Invalid login rejection  
3. Audio upload refinement  
4. Typed findings to report generation  
5. Save report to database  
6. Search by keywords  
7. Admin doctor filter  
8. PDF export  
9. Background task status check  

---

# CHAPTER 8 CONCLUSION AND DISCUSSION

## 8.1 Overall Analysis of Internship / Project Viabilities

The project was technically feasible and practical to implement during the internship period. It combined real backend development, frontend integration, database handling, AI support, and asynchronous workflow management into a single usable system.

## 8.2 Photographs and Date of Surprise Visit by Institute Mentor

As the internship was carried out remotely, this part may be written as:

**The internship and project work were completed in remote mode. Therefore, physical surprise visit photographs were not applicable.**

## 8.3 Dates of Continuous Evaluation (CE-I and CE-II)

This section can be filled manually according to institute records.

## 8.4 Problems Encountered and Possible Solutions

### Problems Encountered

- external API-related issues,  
- report formatting mismatch,  
- authentication and route handling bugs,  
- concurrency-related adjustments,  
- variation in transcription quality,  
- and template-fit issues for different findings.  

### Possible Solutions

- stronger retry handling,  
- better prompt tuning,  
- more template coverage,  
- stronger monitoring,  
- and production-grade deployment practices.  

## 8.5 Summary of Internship / Project Work

The Radiology AI Platform was successfully designed and developed as a full-stack project. It covers authentication, speech-based input, transcript refinement, structured report generation, encrypted storage, report retrieval, search, export, and background processing. The work helped in understanding both software engineering practice and practical AI-assisted system design.

## 8.6 Limitation and Future Enhancement

### Limitations

- dependence on external AI APIs,  
- need for manual review of medical content,  
- limited specialization for every imaging type,  
- and scope for stronger production hardening.  

### Future Enhancement

- more study-specific templates,  
- multilingual support,  
- deeper hospital-system integration,  
- better analytics and monitoring,  
- and stronger recommendation logic for report structure.  

---

# REFERENCES

1. FastAPI Documentation. Available at: https://fastapi.tiangolo.com/  
2. React Documentation. Available at: https://react.dev/  
3. PostgreSQL Documentation. Available at: https://www.postgresql.org/docs/  
4. Redis Documentation. Available at: https://redis.io/docs/  
5. Celery Documentation. Available at: https://docs.celeryq.dev/  
6. Hugging Face Documentation. Available at: https://huggingface.co/docs  
7. Tailwind CSS Documentation. Available at: https://tailwindcss.com/docs  
8. jsPDF Documentation. Available at: https://github.com/parallax/jsPDF  
9. SQLAlchemy Documentation. Available at: https://docs.sqlalchemy.org/  
10. RadReport. Available at: https://radreport.org/  
11. Gujarat Technological University Project Report Guidelines  
12. Relevant articles on speech processing, structured reporting, and AI-assisted medical documentation  

---

# APPENDIX

## Appendix A - Student and Project Details

- **Student Name:** Dev Thakar  
- **Enrollment Number:** 230673107042  
- **College Name:** Sal Institute of Technology and Engineering Research  
- **Address:** App. Science City, Sola Road, Ahmedabad, 380060  
- **Department:** Computer Engineering  
- **Project Title:** Radiology AI Platform  
- **Guide Name:** Komal Thummar  
- **Head of Department:** Dr. Nimisha Patel  
- **University:** Gujarat Technological University  
- **Academic Year:** 2025-26  

## Appendix B - Internship Details

- **Company Name:** FICE Education Pvt. Ltd.  
- **Work Mode:** Remote  
- **Industry Mentor:** Anjali Singh  
- **Start Date:** 21/01/2026  
- **End Date:** 01/04/2026  
- **Duration:** 12 Weeks  

## Appendix C - Core Project Features

- doctor and admin authentication  
- live browser dictation  
- uploaded audio refinement  
- structured report generation from findings  
- encrypted report storage  
- admin report filtering  
- keyword-based report search  
- editable structured report panel  
- PDF export  
- Celery and Redis based background processing  
- Flower-based worker monitoring  
- homepage and reporting dashboard  

## Appendix D - Suggested Diagrams for Final Report

You can add these diagrams in Word if required:

1. System architecture diagram  
2. Use case diagram  
3. Sequence diagram for report generation  
4. Authentication workflow diagram  
5. Database ER diagram  
6. Dashboard screenshots  
7. Audio refinement flow diagram  
8. Structured report generation flow diagram  

---

# IMPORTANT FINAL NOTE

To match `Report_sample.pdf` properly in Word:

- Use **Times New Roman**
- Chapter headings: **16 pt bold uppercase**
- Section headings: **14 pt bold uppercase**
- Subsection headings: **12 pt bold**
- Body text: **12 pt**
- Line spacing: **1.5**
- Margins:
  - Left: **1.25 inch**
  - Right: **1.0 inch**
  - Top: **1.0 inch**
  - Bottom: **1.0 inch**
- Put page numbers at bottom center
- Put preliminary pages in Roman numbering
- Put chapters in Arabic numbering

This Markdown file is the content source. Final formatting should be done manually in Word as per the sample.
