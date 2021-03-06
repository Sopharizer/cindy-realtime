/*
 *
 * WebSocketInterface constants
 *
 */

import {
  SET_CURRENT_USER,
} from 'containers/UserNavbar/constants';

import { PUZZLE_SHOWN, PUZZLE_HID } from 'containers/PuzzleShowPage/constants';

import {
  CHATROOM_CONNECT,
  CHATROOM_DISCONNECT,
  SEND_DIRECTCHAT,
} from 'containers/Chat/constants';

export const INTERNAL_ACTIONS = [
  SET_CURRENT_USER,
  PUZZLE_SHOWN,
  PUZZLE_HID,
  CHATROOM_CONNECT,
  CHATROOM_DISCONNECT,
  SEND_DIRECTCHAT,
];

export const WS_CONNECT = 'app/WebSocketInterface/WS_CONNECT';
export const WS_DISCONNECT = 'app/WebSocketInterface/WS_DISCONNECT';
