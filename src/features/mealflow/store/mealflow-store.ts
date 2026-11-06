import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

import { zustandStorage } from '@/lib/storage';
import type { DeliveryStop, MealFlowState, Volunteer, VoiceUpdate } from '@/features/mealflow/types/mealflow';

const people = [
  'James Carter','Evelyn Brooks','Robert Hamilton','Patricia Lewis','George Martinez',
  'Helen Clark','Thomas Baker','Dorothy Allen','Walter Young','Barbara King',
  'Richard Wright','Margaret Wilson','Joseph Scott','Nancy Green','Charles Adams',
  'Ruth Nelson','Frank Hill','Martha Evans','Henry Collins','Virginia Turner',
];
const streets = [
  '88 Pinecrest Ln','317 Maple St','654 Cedar Ave','901 Walnut Dr','22 Birch St',
  '1767 Sycamore Way','45 Oak Ridge Dr','109 Riverbend Ct','804 Magnolia Ave','63 Willow Ln',
  '412 Elm St','1420 Oak Ridge Dr','733 Spruce Ave','219 Orange St','508 Palm Way',
  '34 Laurel Ct','1260 Canyon Rd','92 Juniper Dr','681 Locust St','305 Redwood Ave',
];
const names = [
  ['David K.','David Kim'],['Sarah T.','Sarah Torres'],['Mike R.','Mike Rivera'],
  ['Lisa M.','Lisa Morgan'],['Kevin S.','Kevin Shah'],['Ana P.','Ana Patel'],
  ['Chris B.','Chris Bell'],['Monica G.','Monica Green'],['Jordan L.','Jordan Lee'],
  ['Rosa D.','Rosa Diaz'],['Patrick W.','Patrick Wong'],['Tina H.','Tina Harris'],
  ['Omar F.','Omar Flores'],['Beth C.','Beth Coleman'],['Sam N.','Sam Nguyen'],
];
const volunteers: Volunteer[] = names.map((name, i) => ({
  id: `v${i + 1}`, name: name[0], status: i < 5 ? 'onRoute' : i < 12 ? 'available' : 'unavailable',
  route: i < 5 ? `Route ${i + 1}` : i < 12 ? 'Standby' : 'Off today',
  hours: 18 + (i * 7) % 34, shifts: 6 + (i * 3) % 12,
  rating: (4.7 + (i % 4) * 0.1).toFixed(1), phone: `555-01${String(i + 10).padStart(2, '0')}`,
}));
const stops: DeliveryStop[] = people.map((recipient, i) => ({
  id: `s${i + 1}`, number: i + 1, recipient, address: streets[i], city: 'Riverside, CA',
  eta: `${8 + Math.floor(i / 3)}:${String((12 + i * 7) % 60).padStart(2, '0')} AM`, meals: i === 2 || i === 11 ? 2 : 1,
  ownerId: i === 5 ? null : `v${(i % 5) + 1}`,
  status: i < 4 ? 'delivered' : i === 4 ? 'delayed' : i === 10 ? 'enRoute' : 'open',
  contact: i < 4 ? 'Reached · delivered' : i === 4 ? 'Reached · running late' : 'Not contacted',
  updatedAt: i < 4 ? `${8 + i}:1${i} AM` : i === 4 ? '9:28 AM' : null, note: '',
}));
const updates: VoiceUpdate[] = [
  { id: 'u1', transcript: 'George Martinez says he is running about ten minutes behind.', stopId: 's5', time: '9:28 AM', outcome: 'Marked delayed' },
  { id: 'u2', transcript: 'James Carter meal delivered. Recipient answered the door.', stopId: 's1', time: '8:12 AM', outcome: 'Delivery confirmed' },
];

export const useMealFlowStore = create<MealFlowState>()(persist((set) => ({
  stops,
  volunteers,
  updates,
  setAvailability: (volunteerId, status) => set((state) => ({
    volunteers: state.volunteers.map((volunteer) => volunteer.id === volunteerId
      ? { ...volunteer, status, route: status === 'unavailable' ? 'Off today' : status === 'available' ? 'Standby' : volunteer.route }
      : volunteer),
  })),
  reassignStop: (stopId, ownerId) => set((state) => ({
    stops: state.stops.map((stop) => stop.id === stopId ? { ...stop, ownerId, note: `Owner updated ${new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}` } : stop),
  })),
  setStopStatus: (stopId, status, note = '') => set((state) => ({
    stops: state.stops.map((stop) => stop.id === stopId ? {
      ...stop, status, contact: status === 'delivered' ? 'Reached · delivered' : status === 'delayed' ? 'Reached · running late' : status === 'enRoute' ? 'Reached · on the way' : stop.contact,
      updatedAt: new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }), note,
    } : stop),
  })),
  addVoiceUpdate: (transcript, stopId, status, note) => set((state) => {
    const time = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    const stop = state.stops.find((item) => item.id === stopId);
    const update: VoiceUpdate = { id: `u${Date.now()}`, transcript, stopId, time, outcome: `Updated ${stop?.recipient ?? 'stop'}` };
    return {
      stops: state.stops.map((item) => item.id === stopId ? {
        ...item, status, contact: status === 'delivered' ? 'Reached · delivered' : status === 'delayed' ? 'Reached · running late' : status === 'enRoute' ? 'Reached · on the way' : 'No answer · follow up',
        updatedAt: time, note,
      } : item),
      updates: [update, ...state.updates],
    };
  }),
}), { name: 'mealflow', storage: createJSONStorage(() => zustandStorage), version: 1 }));
