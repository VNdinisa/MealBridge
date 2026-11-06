export type StopStatus = 'delivered' | 'enRoute' | 'delayed' | 'open';
export type VolunteerStatus = 'available' | 'onRoute' | 'unavailable';

export interface DeliveryStop {
  id: string;
  number: number;
  recipient: string;
  address: string;
  city: string;
  eta: string;
  meals: number;
  ownerId: string | null;
  status: StopStatus;
  contact: string;
  updatedAt: string | null;
  note: string;
}

export interface Volunteer {
  id: string;
  name: string;
  status: VolunteerStatus;
  route: string;
  hours: number;
  shifts: number;
  rating: string;
  phone: string;
}

export interface VoiceUpdate {
  id: string;
  transcript: string;
  stopId: string;
  time: string;
  outcome: string;
}

export interface MealFlowState {
  stops: DeliveryStop[];
  volunteers: Volunteer[];
  updates: VoiceUpdate[];
  setAvailability: (volunteerId: string, status: VolunteerStatus) => void;
  reassignStop: (stopId: string, ownerId: string | null) => void;
  setStopStatus: (stopId: string, status: StopStatus, note?: string) => void;
  addVoiceUpdate: (transcript: string, stopId: string, status: StopStatus, note: string) => void;
}
