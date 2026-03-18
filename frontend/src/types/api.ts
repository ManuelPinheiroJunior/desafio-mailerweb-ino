export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type Booking = {
  id: string;
  title: string;
  room_id: string;
  organizer_user_id: string;
  start_at: string;
  end_at: string;
  status: "ACTIVE" | "CANCELED";
  participants: string[];
  version: number;
};

export type Room = {
  id: string;
  name: string;
  capacity: number;
};
