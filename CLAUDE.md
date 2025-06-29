# Emergency Alert System - Claude Assistant Documentation

## 🚨 Current System Status: PRODUCTION READY

### 🏆 Achieved Milestones

#### ✅ Complete Dynamic Emergency Response Pipeline
- **Sonoff Device Control**: 3-cycle blink sequence ending OFF
- **Intelligent Text Alerts**: AI-generated context-aware messages  
- **Dynamic Emergency Images**: Real-time generation with incident data
- **Voice Messages**: OpenAI TTS in Spanish with emergency details
- **Animated Emergency GIFs**: Dynamic spinning siren with real data

#### ✅ Flexible SOS Trigger System
- **Pattern Recognition**: Any combination of SOS (sos, S.O.S, etc.)
- **Incident Extraction**: Max 2 words after SOS become emergency title
- **Examples**: "SOS INCENDIO" → "INCENDIO", "SOS EMERGENCIA MÉDICA" → "EMERGENCIA MÉDICA"

#### ✅ AI-Powered Emergency Messaging
- **Context-Aware Alerts**: Specific safety instructions per incident type
- **Professional Formatting**: Appropriate emojis and WhatsApp optimization
- **Intelligent Voice Content**: TTS-optimized emergency broadcasts
- **Fallback Protection**: Always sends alerts even if AI fails

#### ✅ Dynamic Group Chat Integration
- **Real Group Names**: Extracts actual WhatsApp group names from webhooks
- **Context-Aware Media**: Images and GIFs show real group context
- **Multiple Webhook Support**: Handles all WHAPI.cloud webhook formats

### 🎯 Current Pipeline Order
1. **Device Blink** (immediate physical alert)
2. **Text Summary** (fast digital alert)
3. **Emergency Image** (visual alert with real data)
4. **Voice Message** (audio broadcast)
5. **Animated GIF** (attention-grabbing visual)

---

## 🚀 PROPOSED: Advanced Member Database System

### 🎯 Vision: Professional Emergency Management Platform

Transform the current alert system into a comprehensive emergency management platform with real member data, intelligent admin tools, and AI-powered natural language commands.

### 🏗️ System Architecture

#### **Data Storage Layer**
- **Google Drive Integration**: Cloud-based member data storage
- **Per-Group JSON Files**: Individual member databases per WhatsApp group
- **Encrypted Sensitive Data**: Medical conditions and emergency contacts
- **Version Control**: Automatic backup and change tracking

#### **AI Command Interface**
- **Natural Language Processing**: GPT-4 powered command interpretation
- **Admin Controls**: Role-based permission system
- **Smart Data Extraction**: Intelligent field mapping and validation

#### **Member Data Schema**
```json
{
  "group_id": "120363400467632358@g.us",
  "group_name": "TEST_ALARM",
  "last_updated": "2024-06-29T10:30:00Z",
  "admins": ["56940035815"],
  "members": {
    "56940035815": {
      "name": "Waldo Rodriguez",
      "alias": ["waldo", "wal"],
      "address": {
        "street": "Av. Las Condes 2024",
        "apartment": "Apt 15B", 
        "floor": "15",
        "neighborhood": "Las Condes",
        "city": "Santiago",
        "coordinates": {"lat": -33.123, "lng": -70.456}
      },
      "contacts": {
        "primary": "+56940035815",
        "emergency": "+56912345678",
        "family": "Ana Rodriguez +56987654321"
      },
      "medical": {
        "conditions": ["diabetes tipo 1"],
        "medications": ["insulin"],
        "allergies": ["penicillin"],
        "blood_type": "O+"
      },
      "emergency_info": {
        "is_admin": true,
        "response_role": "coordinator",
        "evacuation_assistance": false,
        "special_needs": []
      },
      "metadata": {
        "joined_date": "2024-01-15",
        "last_active": "2024-06-29",
        "data_version": "1.2"
      }
    }
  }
}
```

### 🎮 Command System

#### **Activation Pattern**
```
@editar [activates editing mode]
@editar [action] [member] [data]
```

#### **Example Commands**
```
@editar dirección waldo a Av. Providencia 123, Las Condes
@editar teléfono emergencia maria a +56912345678
@editar admin agregar carlos  
@editar condición médica ana diabetes tipo 1
@editar alias juan a juanito
@editar evacuar ayuda pedro requiere asistencia
```

#### **AI Command Processing Flow**
1. **Command Detection**: Recognize @editar patterns
2. **Admin Verification**: Check user permissions
3. **GPT Interpretation**: Extract action, member, and data
4. **Data Validation**: Verify format and completeness
5. **File Update**: Modify member database
6. **Cloud Sync**: Update Google Drive
7. **Confirmation**: Send success/error message

### 🚨 Enhanced Emergency Response

#### **Before (Current)**
```
🚨 EMERGENCIA: INCENDIO
📍 Ubicación por confirmar
👤 Waldo  
📞 56940035815
```

#### **After (With Member Database)**
```
🚨 INCENDIO REPORTADO 🔥
📍 Av. Las Condes 2024, Apt 15B (Piso 15)
👤 Waldo Rodriguez (Admin del grupo)
📞 Principal: +56940035815 | Emergencia: +56912345678
⚕️ Condiciones médicas: Diabetes tipo 1
🩸 Tipo de sangre: O+
👨‍👩‍👧‍👦 Contacto familiar: Ana Rodriguez +56987654321
🚨 Bomberos: Ruta optimizada por ubicación exacta
🏥 Hospital más cercano: Clínica Las Condes (1.2km)
```

### 📋 Implementation Phases

#### **Phase 1: Core Infrastructure (Week 1-2)**
- [ ] Google Drive API setup and authentication
- [ ] Basic member data file management (CRUD)
- [ ] Simple @editar command parsing
- [ ] Admin permission system
- [ ] Local testing with real credentials

#### **Phase 2: AI Integration (Week 3-4)**
- [ ] GPT-4 command interpretation system
- [ ] Natural language data extraction
- [ ] Command validation and error handling
- [ ] Comprehensive admin controls

#### **Phase 3: Emergency Integration (Week 5-6)**
- [ ] Real-time member data lookup during emergencies
- [ ] Enhanced emergency message generation
- [ ] Medical condition aware responses
- [ ] Location-based emergency routing

#### **Phase 4: Advanced Features (Week 7-8)**
- [ ] Bulk import/export functionality
- [ ] Data encryption for sensitive information
- [ ] Audit logging and change tracking
- [ ] Backup and recovery systems

### 🛡️ Security & Privacy

#### **Data Protection**
- **Encryption**: Sensitive medical data encrypted at rest
- **Access Control**: Role-based permissions (admin, moderator, member)
- **Audit Logging**: All changes tracked with timestamps and user IDs
- **GDPR Compliance**: Data minimization and user consent frameworks

#### **Permission Levels**
- **Admin**: Full edit access, user management, bulk operations
- **Moderator**: Basic member info editing, no sensitive data
- **Member**: View own data, request changes

### 🎯 Success Metrics

#### **Operational Improvements**
- **Response Time**: Reduce emergency response coordination by 60%
- **Data Accuracy**: 100% real member addresses vs 0% placeholders
- **Medical Awareness**: Include medical conditions in 100% of relevant emergencies
- **Admin Efficiency**: Natural language commands reduce data entry time by 80%

#### **System Capabilities**
- **Real Emergency Data**: Complete member profiles with addresses, medical info
- **Intelligent Routing**: Location-aware emergency service coordination
- **Medical Emergency Support**: Condition-specific response protocols
- **Professional Grade**: Enterprise-level emergency management features

---

## 🔧 Development Guidelines

### **Testing Approach**
1. **Local Testing**: Use Google Drive credentials for safe local development
2. **Isolated Environment**: Separate test group and member data
3. **Gradual Rollout**: Phase implementation with fallback systems
4. **User Feedback**: Collect admin input throughout development

### **Code Organization**
```
app/
├── services/
│   ├── gdrive_service.py          # Google Drive integration
│   ├── member_database_service.py # Member data management
│   ├── ai_command_service.py      # GPT command processing
│   └── emergency_lookup_service.py # Real-time member lookup
├── models/
│   ├── member_models.py           # Member data schemas
│   └── command_models.py          # Command parsing models
└── utils/
    ├── encryption_utils.py        # Data encryption utilities
    └── validation_utils.py        # Data validation helpers
```

### **Integration Points**
- **Emergency Pipeline**: Enhance `create_full_emergency_pipeline.py`
- **Command Processor**: Extend `command_processor.py` with @editar handlers
- **Message Generation**: Update AI message templates with real data
- **Webhook Processing**: Add member lookup to WhatsApp message parsing

---

## 📚 Command Reference

### **Current Commands**
- `SOS [incident]` - Trigger emergency response with optional incident type
- `SOS` - Trigger general emergency response

### **Proposed Commands**
- `@editar` - Activate member data editing mode
- `@editar [action] [member] [data]` - Update member information
- `@ver [member]` - View member information (admin only)
- `@lista` - List all group members (admin only)
- `@backup` - Create manual backup of member data
- `@importar [file]` - Import bulk member data (admin only)

---

## 🎯 Next Steps

1. **Obtain Google Drive Credentials**: Set up API access for local testing
2. **Create Test Member Database**: Build sample data structure for development
3. **Implement Phase 1**: Basic Google Drive integration and file management
4. **Test Command Parsing**: Develop and test @editar command recognition
5. **Integrate with Emergency System**: Connect member lookup to alert generation

---

*Last Updated: 2024-06-29*  
*Status: Member Database System - Planning Phase*  
*Emergency System: Production Ready*