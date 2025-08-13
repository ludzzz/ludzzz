# SRE Team Book of Work

## 1. Team Charter

### Mission
Enable the support team to shift from reactive firefighting to proactive problem-solving by providing robust, scalable engineering solutions and frameworks.

### Vision
Transform support operations from manual interventions to automated, self-healing systems that prevent issues before they impact users.

### Core Objectives
- Build tooling and automation to reduce manual support work
- Establish engineering best practices for sustainable operations  
- Create frameworks that scale across supported teams
- Enable support team to focus on complex problems vs. repetitive tasks

### Success Metrics
- Reduced manual intervention tickets
- Decreased mean time to resolution (MTTR)
- Increased automation coverage
- Support team satisfaction with available tools

### Scope
**IN SCOPE:**
- Tooling, automation, frameworks, operational procedures
- Platform services and developer frameworks

**OUT OF SCOPE:**
- Direct customer support
- Business logic development

### Key Stakeholders
- **Primary:** Support team
- **Secondary:** Development teams we support

---

## 2. Service Inventory

### Existing Services
- **Python Repository Framework** - Standardized repo template with testing, type checking, CI/CD pipeline, Artifactory integration

### Planned Services

#### Core Infrastructure
- **Hydra** - Asset management web service (JIRA Asset golden source + extended DB properties)
- **Container Platform** - On-premise containerization (evaluating Packer + Nomad)
- **JAMS Replacement** - New job scheduling solution

#### Developer/Support Tools
- **Slack Bot Framework** - Self-service bot creation toolkit for support teams
- **RFBD** - Report For Business Dashboard (morning checks + health monitoring UI)

#### Integrations
- **Third-party Monitoring** - Implementation support for chosen monitoring tool (ITRS/AppDynamics)

### Service Categories
- **Platform Services**: Hydra, Container Platform, JAMS replacement
- **Developer Frameworks**: Python repo template, Slack bot framework  
- **Operational Tools**: RFBD, monitoring integrations

### Priority Delivery Order
1. **Hydra** (Major Delivery - foundational asset data)
2. **RFBD** (immediate operational value)
3. **Container Platform** (infrastructure modernization)
4. **Slack Bot Framework** (support team productivity)
5. **JAMS Replacement** (legacy system modernization)
6. **Third-party Monitoring** (operational excellence)

---

## 3. Major Delivery Focus: Hydra

### Strategic Importance
- **Foundational** - Other services will need asset/ownership data
- **High Visibility** - Addresses core operational pain point
- **Credibility Builder** - Early win with support team

### Technical Architecture
- **Data Sources**: JIRA Asset (golden source) + Extended properties database
- **Interface**: Web service with REST API
- **Frontend**: Web UI for asset management
- **Integration**: API endpoints for other internal services

### Key Features
#### Phase 1 - MVP
- Basic JIRA Asset query interface
- Read-only asset information display
- Simple web UI for asset lookup

#### Phase 2 - Core Platform
- Extended properties database
- CRUD operations for additional asset details
- Asset ownership management
- Data synchronization with JIRA Asset

#### Phase 3 - Integration Platform
- REST API for service consumption
- Automation hooks and webhooks
- Integration with monitoring tools
- Bulk operations and reporting

### Critical Success Factors

#### Technical
- API design for easy consumption by other tools
- Data sync strategy with JIRA Asset (real-time vs batch)
- Database schema for extended properties
- Authentication/authorization model
- Performance and scalability considerations

#### Operational
- Data governance - who can update what
- SLA for data freshness/accuracy (target: 99.5% uptime, <5min data lag)
- Migration plan from current asset tracking methods
- Backup and disaster recovery procedures

#### Stakeholder Management
- Support team input on required properties/workflows
- Asset owners' responsibility for data accuracy
- Integration touchpoints with existing tools
- Training and documentation for end users

### Delivery Roadmap
| Milestone | Timeline | Deliverables |
|-----------|----------|--------------|
| **Discovery** | Month 1 | Requirements gathering, technical design |
| **MVP** | Month 2-3 | Basic JIRA Asset integration, simple UI |
| **Core Platform** | Month 4-6 | Extended properties, full CRUD, sync |
| **Integration Platform** | Month 7-8 | APIs, automation, monitoring integration |

### Risk Mitigation
- **Start Small**: Begin with critical asset types only
- **API Dependencies**: Plan for JIRA Asset API limitations/downtime
- **Data Quality**: Implement validation and rollback strategies
- **User Adoption**: Ensure support team involvement in design process

---

## 4. Responsibilities Matrix

### Team Structure
- **SRE Lead**: Strategy, stakeholder management, architecture decisions
- **Senior SRE**: Technical design, complex implementation, mentoring
- **SRE Engineers**: Development, testing, documentation, support

### Responsibility Areas

#### Development & Engineering
- **RACI**: SRE Team (R,A), Support Team (C), Dev Teams (I)
- Code development, testing, deployment automation
- Architecture decisions and technical documentation

#### Operations & Maintenance
- **RACI**: SRE Team (R,A), Support Team (C,I)
- Service monitoring, incident response for SRE services
- Performance optimization and capacity planning

#### Support & Training
- **RACI**: SRE Team (R,A), Support Team (C), End Users (I)
- User documentation, training materials
- Level 2 support for SRE-built tools

---

## 5. Success Metrics & KPIs

### Team-Level Metrics
- **Service Availability**: 99.5% uptime for critical services
- **Delivery Velocity**: On-time delivery of planned features
- **User Satisfaction**: Quarterly surveys with support team
- **Technical Debt**: Reduction in manual processes by 50%

### Service-Specific Metrics (Hydra)
- **Data Accuracy**: 99% asset data accuracy vs. JIRA Asset
- **API Performance**: <200ms average response time
- **Usage Adoption**: 80% of support team using Hydra within 6 months
- **Integration Success**: 3+ internal services consuming Hydra API

### Operational Impact
- **Incident Reduction**: 30% fewer asset-related support tickets
- **Resolution Time**: 25% faster incident resolution with better asset data
- **Automation Coverage**: 60% of asset queries automated

---

## 6. Communication & Reporting

### Stakeholder Updates
- **Weekly**: Progress updates to support team leadership
- **Bi-weekly**: Technical reviews with development teams
- **Monthly**: Executive summary to senior leadership
- **Quarterly**: Comprehensive metrics and roadmap review

### Documentation Standards
- **Technical**: Architecture decisions, API documentation, runbooks
- **User**: Training materials, troubleshooting guides, FAQs
- **Process**: Change management, incident response, deployment procedures

---

*Document Version: 1.0*  
*Last Updated: August 2025*  
*Owner: SRE Team Lead*