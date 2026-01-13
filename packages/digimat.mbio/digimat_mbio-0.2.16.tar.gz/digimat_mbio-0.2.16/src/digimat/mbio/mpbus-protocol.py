import logging
from typing import List, Tuple, Optional

import socket
import struct
import time
from typing import Optional
import logging


class MPBusErrorException(Exception):
    """Base pour toutes les erreurs spécifiques au protocole MP-Bus."""
    def __init__(self, message: str, raw_frame: Optional[bytes] = None):
        super().__init__(message)
        self.raw_frame = raw_frame

class MPTransportError(MPBusErrorException):
    """
    Échec de la communication réseau (connexion/socket) avec le gateway distant.
    Déclenche une répétition (sauf si MPBusMaster l'arrête).
    """
    pass

class MPProtocolError(MPBusErrorException):
    """
    Échec Layer 1/2 : Timeout [trep] / Parité/Checksum incorrect / Longueur de trame invalide.
    Déclenche une répétition.
    """
    pass

class MPApplicationError(MPBusErrorException):
    """
    L'esclave répond avec le bit d'erreur Layer 7 positionné [Error Bit].
    Contient le code d'erreur applicatif renvoyé.
    """
    def __init__(self, message: str, error_code: int, raw_frame: Optional[bytes] = None):
        super().__init__(message, raw_frame)
        self.error_code = error_code

class MPAccessDenied(MPApplicationError):
    """
    Erreur critique : Code d'erreur 12 [Code 12].
    Doit signaler au contrôleur d'arrêter la boucle de répétition.
    """
    pass

class MPUnknownCommand(MPApplicationError):
    """
    Code d'erreur 11 (Unknown command) [Code 11].
    """
    pass


class MPUtils:
    MP_MODE_ADDRESSED = 0b001  # Mode adressé/OnEvent
    MP_MODE_BROADCAST = 0b000  # Mode Broadcast
    #MASTER_START_BYTE_MASK = 0b10000000  # Bit de poids fort toujours à 1 pour le Startbyte Maître
    MASTER_START_BYTE_MASK = 0x10  # Bit de poids fort toujours à 1 pour le Startbyte Maître

    @classmethod
    def calculate_crossparity(cls, data_bytes: List[int]) -> int:
        cp = 0
        # Le nombre d'octets à traiter est (N + 1)
        # N est codé dans les bits 3-5 du Startbyte (index 0)
        num_bytes = ((data_bytes[0] & 0x70) >> 4) + 1

        for i in range(num_bytes):
            byte = data_bytes[i]
            # Calcul de la parité paire : 1 si le compte de '1' est impair
            parity_bit = bin(byte).count('1') % 2

            # Décalage vers la droite et insertion du bit dans le MSB (bit 7)
            cp = (cp >> 1) | (parity_bit << 7)

        return cp & 0xff

    @classmethod
    def calculate_lengthparity(cls, data_bytes: List[int], cp_byte: int) -> int:
        """
        Implémente le Checksum Layer 2 par XOR de tous les octets précédents.
        """
        lp = 0

        # On XOR d'abord tous les octets de données (Startbyte inclus)
        for byte in data_bytes:
            lp ^= byte

        # On XOR enfin le résultat avec l'octet de Crossparity
        lp ^= cp_byte

        return lp & 0xff

    @classmethod
    def build_mp_frame(cls, mode: int, address_code: int, command_code: int, parameters: List[int]) -> bytes:
        """
        Construit une trame Maître MP-Bus complète, incluant Startbyte, Layer 2 Checksum.
        """
        # 1. Calculer N (Nombre d'octets de données: Command Code + Parameters)
        N = 1 + len(parameters)

        if N < 1 or N > 7:
            raise ValueError("Le nombre d'octets de données (C + P) doit être entre 1 et 7.")

        # 2. Calculer le Startbyte Maître (stb)
        # Convention NNN (bits 3 à 5): NNN = N - 1 (de 0 à 6)
        stb_data_length = N - 1
        start_byte = MPUtils.MASTER_START_BYTE_MASK | ((stb_data_length & 0x07) << 3) | (address_code & 0x07)

        # 3. Assembler les octets de données brutes
        data_bytes = [start_byte, command_code] + parameters

        # 4. Calculer la Crossparity (cp)
        cp = cls.calculate_crossparity(data_bytes)

        # 5. Calculer la Lengthparity (lp)
        lp = cls.calculate_lengthparity(data_bytes, cp)

        # 6. Assembler la trame complète
        frame_list = data_bytes + [cp, lp]

        return bytes(frame_list)

    @classmethod
    def validate_mp_frame(cls, raw_answer_bytes: bytes) -> Tuple[bool, int, bytes]:
        """
        Vérifie la Crossparity et la Lengthparity de la réponse reçue, et le bit d'erreur Layer 7.
        Returns: Tuple (is_error_bit_set, error_code_if_set, data_bytes)
        """
        if len(raw_answer_bytes) < 3: # Min: Startbyte + CP + LP
            raise MPProtocolError(f"Réponse trop courte ({len(raw_answer_bytes)} octets).")

        stb_slave = raw_answer_bytes[0]

        # 1. Vérification du Startbyte Esclave (stb) - MSB doit être 0
        if stb_slave & 0x80 != 0:
            raise MPProtocolError("Le bit de poids fort du Startbyte Esclave est incorrect (devrait être 0).")

        # 2. Décodage longueur
        data_length_bytes = (stb_slave & 0x07) + 1 # N

        expected_length = 1 + data_length_bytes + 1 + 1

        if len(raw_answer_bytes) != expected_length:
            # Gestion trame d'erreur courte (souvent 4 octets)
            if len(raw_answer_bytes) == 4 and (stb_slave & 0x80) == 0:
                error_code = raw_answer_bytes[1]
                is_protocol_ok, error_code_checked = cls._check_parity_checksum(raw_answer_bytes)
                if not is_protocol_ok:
                    raise MPProtocolError(f"Layer 2 invalide dans la trame d'erreur Layer 7.")
                return True, error_code, raw_answer_bytes[1:-2]
            else:
                raise MPProtocolError(f"Longueur de trame invalide. Reçu {len(raw_answer_bytes)}, Attendu {expected_length}.")

        # Vérification CRC Layer 2
        is_protocol_ok, _ = cls._check_parity_checksum(raw_answer_bytes)
        if not is_protocol_ok:
            raise MPProtocolError("Checksum Layer 2 (CP/LP) invalide.")

        # Vérification Bit Erreur Layer 7 (Simulation bit 6 dans STB ou code retour)
        if stb_slave & 0x40 != 0:
            error_code = raw_answer_bytes[1]
            return True, error_code, raw_answer_bytes[1:-2]

        # Extraction données utiles
        data_bytes = raw_answer_bytes[1:1+data_length_bytes]
        return False, 0, data_bytes

    @classmethod
    def _check_parity_checksum(cls, raw_answer_bytes: bytes) -> Tuple[bool, int]:
        """Vérifie CP et LP de la trame reçue."""
        data_and_stb = [b for b in raw_answer_bytes[:-2]]
        cp_received = raw_answer_bytes[-2]
        lp_received = raw_answer_bytes[-1]

        cp_calculated = 0
        for byte in data_and_stb:
            cp_calculated ^= byte

        lp_calculated = cls.calculate_lengthparity(data_and_stb, cp_calculated)

        if cp_received != cp_calculated: return False, 1
        if lp_received != lp_calculated: return False, 2
        return True, 0


class TCPGatewayWrapper:
    """
    Gère la connexion TCP et l'encapsulation/désencapsulation des trames MP brutes.
    Implémentation robuste avec reconnexion automatique, lecture bufferisée et gestion du framing.
    """
    def __init__(self, host: str, port: int, gateway_id: int, logger):
        self.host = host
        self.port = port
        self.gateway_id = gateway_id
        self.logger = logger
        self.socket: Optional[socket.socket] = None
        self._is_connected = False

    def connect(self):
        """Établit la connexion initiale."""
        self._connect_socket()

    def _connect_socket(self):
        """Logique interne de connexion avec gestion d'erreurs et configuration socket."""
        # Nettoyage préventif si reconnexion
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self._is_connected = False

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Options TCP pour la performance (Latence réduite)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            # Timeout de connexion (différent du timeout de réception MP-Bus)
            self.socket.settimeout(5.0)

            self.socket.connect((self.host, self.port))
            self._is_connected = True
            self.logger.info(f"Connecté au gateway TCP à {self.host}:{self.port}")

        except Exception as e:
            self.socket = None
            self._is_connected = False
            self.logger.error(f"Échec de la connexion TCP au gateway: {e}")
            raise MPTransportError(f"Échec de la connexion TCP au gateway: {e}")

    def close(self):
        """Fermeture propre de la connexion."""
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except:
                pass
            self.socket = None
            self._is_connected = False
            self.logger.info("Déconnecté du gateway TCP.")

    def _encapsulate(self, mp_frame: bytes) -> bytes:
        """
        Encapsule la trame MP pour le transport.
        Header: [ID_Gateway (2B Big Endian) | Len_MP (2B Big Endian) | MP_Frame]
        """
        frame_len = len(mp_frame)
        # Utilisation de struct pour garantir le Big Endian (Standard réseau)
        # TODO:
        return mp_frame

        # header = struct.pack('>HH', self.gateway_id, frame_len)
        # return header + mp_frame

    def send_raw(self, mp_frame: bytes) -> None:
        """Envoie une trame avec tentative de reconnexion automatique en cas de tuyau brisé."""
        encapsulated_data = self._encapsulate(mp_frame)

        # Tentative d'envoi avec reconnexion
        for retry in range(2): # 1 essai initial + 1 retry
            try:
                if not self._is_connected or self.socket is None:
                    self._connect_socket()

                self.socket.sendall(encapsulated_data)
                self.logger.debug(f"-> Envoyé trame encapsulée (MP: {mp_frame.hex()})")
                return # Succès

            except (socket.error, BrokenPipeError) as e:
                self.logger.warning(f"Erreur socket à l'envoi ({e}). Tentative de reconnexion ({retry+1}/2)...")
                self._is_connected = False
                # La boucle va retenter _connect_socket() au prochain tour

        # Si échec après retry
        raise MPTransportError(f"Échec de l'envoi après tentatives de reconnexion.")

    def _recv_n_bytes(self, n: int) -> bytes:
        """
        Lit exactement n octets du socket.
        Gère la fragmentation TCP (lecture en plusieurs fois si nécessaire).
        """
        data = b''
        while len(data) < n:
            try:
                # On demande le reste des données manquantes
                chunk = self.socket.recv(n - len(data))
                if not chunk:
                    # Socket fermé par le distant (EOF)
                    raise MPTransportError("Connexion fermée par le distant (EOF) pendant la réception.")
                data += chunk
            except socket.timeout:
                # Le timeout est propagé pour être géré comme un timeout MP-Bus (trep)
                raise
            except socket.error as e:
                self._is_connected = False
                raise MPTransportError(f"Erreur de lecture socket bas niveau: {e}")
        return data

    def receive_raw(self, timeout_ms: int) -> bytes:
        """
        Reçoit une réponse complète en gérant le framing (Header + Payload).
        Gère le timeout spécifique MP-Bus (trep).
        """
        if not self._is_connected or not self.socket:
            raise MPTransportError("Le socket n'est pas connecté.")

        timeout_s = timeout_ms / 1000.0
        self.socket.settimeout(timeout_s)

        try:
            # TODO:

            """
            # 1. Lecture du Header (4 octets) : ID + Longueur
            # Cette lecture bloque jusqu'à recevoir 4 octets ou timeout
            header_data = self._recv_n_bytes(4)

            # Décodage header avec struct (>HH = Big Endian, 2 unsigned short)
            gateway_id, mp_frame_len = struct.unpack('>HH', header_data)

            # Vérification de l'ID Gateway
            if gateway_id != self.gateway_id:
                self.logger.warning(f"ID Gateway inattendu dans la réponse: {gateway_id} != {self.gateway_id}")
            """
            header_data = self._recv_n_bytes(2)
            mp_frame_len, = struct.unpack('>H', header_data)

            # 2. Lecture du payload (MP Frame) basée sur la longueur décodée
            if mp_frame_len > 0:
                mp_frame = self._recv_n_bytes(mp_frame_len)
            else:
                mp_frame = b''

            self.logger.debug(f"<- Reçu (MP: {mp_frame.hex()})")
            return mp_frame

        except socket.timeout:
            # C'est un comportement normal du protocole MP-Bus (pas de réponse de l'esclave)
            # On lève une erreur protocolaire pour déclencher la logique de répétition
            raise MPProtocolError(f"Timeout (trep={timeout_ms}ms) atteint lors de la réception.")

        except MPTransportError as e:
            # Erreur critique de transport (déconnexion, etc.)
            self._is_connected = False
            raise e

        except Exception as e:
            # Autres erreurs imprévues
            self._is_connected = False
            raise MPTransportError(f"Erreur fatale de réception: {e}")


class MPBusTransport:
    """Orchestre l'échange de trames brutes et gère les timings trep."""

    TIMEOUT_MS_ADDRESSED = 600+150
    TIMEOUT_MS_BROADCAST = 150+150

    def __init__(self, wrapper: TCPGatewayWrapper):
        self.wrapper = wrapper

    def transact(self, command_frame: bytes, mode: int) -> bytes:
        """
        Envoie une trame de commande et attend une réponse, en appliquant le timeout approprié.
        """
        timeout_ms = self.TIMEOUT_MS_BROADCAST
        if mode == MPUtils.MP_MODE_ADDRESSED:
            timeout_ms = self.TIMEOUT_MS_ADDRESSED

        self.wrapper.send_raw(command_frame)

        if mode == MPUtils.MP_MODE_BROADCAST:
            # En mode Broadcast, la librairie Maître n'attend pas de réponse
            # Petit délai pour laisser le temps au gateway de traiter
            time.sleep(0.01)
            return b''

        return self.wrapper.receive_raw(timeout_ms)


class MPBusMasterController:
    """
    Cœur de la logique Maître : gère la robustesse, les répétitions, le logging et l'Application Layer.
    """

    MAX_ATTEMPTS = 3

    def __init__(self, transport: MPBusTransport, logger: logging.Logger):
        self.transport = transport
        self.logger = logger

    def send_command(self, command_frame: bytes, mode: int, address: int) -> bytes:
        last_exception: Optional[MPBusErrorException] = None
        attempt = 0

        while attempt < self.MAX_ATTEMPTS:
            attempt += 1
            try:
                if attempt > 1:
                    self.logger.warning(f"Répétition: Tentative {attempt}/{self.MAX_ATTEMPTS} pour adresse {address}")

                # 1. Transport et Timing
                raw_answer = self.transport.transact(command_frame, mode)

                if mode == MPUtils.MP_MODE_BROADCAST:
                    return b''

                # 2. Validation Layer 2 et Layer 7
                is_error_layer7, error_code, data_bytes = MPUtils.validate_mp_frame(raw_answer)

                if is_error_layer7:
                    self.logger.debug(f"Erreur Layer 7 (Code {error_code}) reçue.")

                    if error_code == 12: # MPAccessDenied
                        self.logger.error(f"Erreur critique MPAccessDenied (Code 12). Arrêt.")
                        raise MPAccessDenied(f"Accès refusé (Code 12) à l'adresse {address}.", error_code, raw_answer)

                    if error_code == 11: # MPUnknownCommand
                        raise MPUnknownCommand(f"Commande inconnue (Code 11) à l'adresse {address}.", error_code, raw_answer)

                    raise MPApplicationError(f"Erreur applicative Layer 7 (Code {error_code}).", error_code, raw_answer)

                # 3. Succès
                if attempt > 1:
                    self.logger.warning(f"Succès après {attempt} tentatives.")
                return data_bytes

            except (MPTransportError, MPProtocolError) as e:
                # Échecs Layer 1/2 -> Répétition
                last_exception = e
                self.logger.debug(f"Échec Layer 1/2 (Répétition): {e}")

                if attempt == self.MAX_ATTEMPTS:
                    self.logger.error(f"Échec persistant à l'adresse {address} après {self.MAX_ATTEMPTS} tentatives.")
                    raise last_exception

            except MPApplicationError as e:
                # Échecs Layer 7 -> Pas de répétition (sauf AccessDenied géré plus haut)
                self.logger.error(f"Échec Layer 7 non répétable: {e}")
                raise e

        if last_exception:
            raise last_exception
        raise MPBusErrorException(f"Condition de sortie inattendue pour adresse {address}.")


class MPBusAPI:
    """
    Implémentation complète des commandes Application Layer (Layer 7) pour le protocole MP-Bus.
    Source de vérité : A91613-100 MP-Cooperation.pdf
    """

    MP_CMD_PEEK = 0x01
    MP_CMD_POKE = 0x02
    MP_CMD_AD_CONVERT = 0x04
    MP_CMD_GET_STATE = 0x0A         # 10
    MP_CMD_GET_STRESS = 0x0B        # 11
    MP_CMD_GET_SETTINGS = 0x0C      # 12
    MP_CMD_GET_MP_ADDRESS = 0x0D    # 13
    MP_CMD_SET_FORCED = 0x0E        # 14
    MP_CMD_SET_EXT_EVENT = 0x0F     # 15
    MP_CMD_GET_MOD_CONFIG = 0x11    # 17
    MP_CMD_GET_MASK = 0x18          # 24 (Malfunction/Maintenance Mask)
    MP_CMD_GET_ERR_STATE = 0x1A     # 26 (Malfunction/Maintenance State)
    MP_CMD_GET_SWITCH = 0x1C        # 28
    MP_CMD_RESET_ERR = 0x1D         # 29
    MP_CMD_GET_VSETTINGS = 0x1E     # 30
    MP_CMD_GET_TRANSIT_TIME = 0x20  # 32
    MP_CMD_START_ADAPTION = 0x21    # 33
    MP_CMD_SET_RELATIVE = 0x25      # 37
    MP_CMD_SET_MP_ADDRESS = 0x26    # 38
    MP_CMD_GET_RELATIVE = 0x29      # 41
    MP_CMD_SET_TRANSIT_TIME = 0x2E  # 46
    MP_CMD_GET_SERIES_NO = 0x32     # 50
    MP_CMD_GET_VRELATIVE = 0x39     # 57
    MP_CMD_SET_OP_RANGE = 0x3A      # 58
    MP_CMD_GET_MIN_MID_MAX = 0x3B   # 59
    MP_CMD_SET_MIN_MID_MAX = 0x3D   # 61
    MP_CMD_SET_SYNC = 0x41          # 65
    MP_CMD_GET_EXT_EVENT = 0x45     # 69
    MP_CMD_GET_STR_ADDR = 0x47      # 71
    MP_CMD_GET_FORCED = 0x4B        # 75
    MP_CMD_LOGIN = 0x4E             # 78
    MP_CMD_GET_FIRMWARE = 0x52      # 82
    MP_CMD_START_TEST_FIRE = 0x56   # 86
    MP_CMD_SET_WATCHDOG = 0x5B      # 91
    MP_CMD_GET_WATCHDOG = 0x5C      # 92
    MP_CMD_SET_SPECIAL = 0x66       # 102
    MP_CMD_SET_DATA = 0x6E          # 110
    MP_CMD_GET_DATA = 0x6F          # 111
    MP_CMD_SET_NEXTBLOCK = 0x70     # 112
    MP_CMD_GET_NEXTBLOCK = 0x71     # 113

    def __init__(self, controller: MPBusMasterController, logger: logging.Logger):
        self.controller = controller
        self.logger = logger
        self.address_cache: List[Tuple[int, bytes]] = []

    # --- Utilitaires Internes ---

    def _int_to_bytes(self, value: int, length: int) -> List[int]:
        """Convertit un entier en liste d'octets (Little Endian)."""
        return list(value.to_bytes(length, byteorder='little'))

    def _bytes_to_int(self, data: bytes) -> int:
        """Convertit des octets en entier (Little Endian)."""
        return int.from_bytes(data, byteorder='little')

    # --- 6.1 Commandes de contrôle d'actionneur ---

    def peek(self, address: int, memory_address: int, length: int) -> bytes:
        """
        [Code 1] MP_Peek: Lit 'length' octets à partir de 'memory_address'.
        Max 7 octets.
        """
        if not (0 < length <= 7):
            raise ValueError("Peek length must be between 1 and 7.")
        params = self._int_to_bytes(memory_address, 2) + [length]
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_PEEK, params)
        return self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def poke(self, address: int, memory_address: int, data: bytes) -> None:
        """
        [Code 2] MP_Poke: Ecrit des données en mémoire RAM/EEPROM.
        Max 4 octets. Réservé outils/config.
        """
        if len(data) > 4:
            raise ValueError("Poke data max length is 4 bytes.")
        params = self._int_to_bytes(memory_address, 2) + list(data)
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_POKE, params)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_settings(self, address: int) -> bytes:
        """
        [Code 12] MP_Get_Settings: Lit les réglages (direction, mode...).
        Retourne 6 octets.
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_SETTINGS, [])
        return self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def set_forced_control(self, address: int, zf: int) -> None:
        """
        [Code 14] MP_Set_Forced_Control: Active une fonction forcée.
        zf: 0=None, 1=Open, 2=Close, 3=Max, 4=Min, etc.
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_FORCED, [zf])
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_modul_configuration(self, address: int) -> bytes:
        """
        [Code 17] MP_Get_Modul_Configuration: Lit la config des modules SW (unités temps/course).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_MOD_CONFIG, [])
        return self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_switch(self, address: int) -> Tuple[int, int, int]:
        """
        [Code 28] MP_Get_Switch: Lit les seuils et l'état des soft-switches.
        Retourne (SwitchPointS1, SwitchPointS2, SwitchState).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_SWITCH, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 5:
            raise MPProtocolError("Réponse MP_Get_Switch trop courte.")
        s1 = self._bytes_to_int(resp[0:2])
        s2 = self._bytes_to_int(resp[2:4])
        state = resp[4]
        return s1, s2, state

    def get_v_settings(self, address: int) -> Tuple[int, int, int]:
        """
        [Code 30] MP_Get_Vsettings: Lit Vnom, Vmax, Vmin (VAV).
        Retourne (Vnom [m3/h], Vmax [%], Vmin [%]).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_VSETTINGS, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 6:
            raise MPProtocolError("Réponse MP_Get_Vsettings trop courte.")
        vnom = self._bytes_to_int(resp[0:2])
        vmax = self._bytes_to_int(resp[2:4])
        vmin = self._bytes_to_int(resp[4:6])
        return vnom, vmax, vmin

    def get_transit_time(self, address: int) -> Tuple[int, int]:
        """
        [Code 32] MP_Get_Transit_Time: Lit la plage mécanique et le temps de course.
        Retourne (Range, Time).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_TRANSIT_TIME, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        # Bytes 1,2 reserved. Range=3,4. Time=5,6
        if len(resp) < 6:
            raise MPProtocolError("Réponse MP_Get_Transit_Time trop courte.")
        rng = self._bytes_to_int(resp[2:4])
        time = self._bytes_to_int(resp[4:6])
        return rng, time

    def set_relative(self, address: int, setpoint: int) -> None:
        """
        [Code 37] MP_Set_Relative: Définit la consigne (Position, Débit ou Vitesse).
        setpoint: 0..10000 (0.01%).
        """
        params = self._int_to_bytes(setpoint, 2)
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_RELATIVE, params)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_relative(self, address: int) -> Tuple[int, int]:
        """
        [Code 41] MP_Get_Relative: Lit la position actuelle et la consigne actuelle.
        Retourne (ActualPosition [%], Setpoint [%]).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_RELATIVE, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 4:
            raise MPProtocolError("Réponse MP_Get_Relative trop courte.")
        actual = self._bytes_to_int(resp[0:2])
        sp = self._bytes_to_int(resp[2:4])
        return actual, sp

    def get_v_relative(self, address: int) -> Tuple[int, int]:
        """
        [Code 57] MP_Get_VRelative: Lit le débit relatif actuel et la consigne.
        Retourne (ActualFlow [%Vnom], Setpoint [%]).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_VRELATIVE, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 4:
            raise MPProtocolError("Réponse MP_Get_VRelative trop courte.")
        actual = self._bytes_to_int(resp[0:2])
        sp = self._bytes_to_int(resp[2:4])
        return actual, sp

    def get_min_mid_max(self, address: int) -> Tuple[int, int, int]:
        """
        [Code 59] MP_Get_Min_Mid_Max: Lit les limites configurées.
        Retourne (Min, Mid, Max) en 0.01%.
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_MIN_MID_MAX, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 6:
            raise MPProtocolError("Réponse MP_Get_Min_Mid_Max trop courte.")
        mn = self._bytes_to_int(resp[0:2])
        mid = self._bytes_to_int(resp[2:4])
        mx = self._bytes_to_int(resp[4:6])
        return mn, mid, mx

    # --- 6.2 Commandes capteurs externes ---

    def ad_convert(self, address: int, choice: int) -> int:
        """
        [Code 4] MP_AD_Convert: Lit une valeur analogique sur l'entrée Y.
        choice: 4=Y(mV), 16=Passive(Ohm 850-1600), 17=Passive(Ohm 200-50k).
        Note: Désactive le contrôle analogique forcé.
        """
        # Param 2 doit toujours être 0xAA selon la doc.
        params = [choice, 0xAA]
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_AD_CONVERT, params)
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 2:
            raise MPProtocolError("Réponse MP_AD_Convert trop courte.")
        return self._bytes_to_int(resp[0:2])

    def get_forced_control_sensor(self, address: int) -> Tuple[int, int]:
        """
        [Code 75] MP_Get_Forced_Control: Lit un switch sur Y et le statut forcé.
        Utilisé pour lire des switches externes. Désactive le contrôle analogique.
        Retourne (zf, zs).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_FORCED, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 2:
            raise MPProtocolError("Réponse MP_Get_Forced_Control trop courte.")
        return resp[0], resp[1]

    # --- 6.3 Commandes de mise en service (Commissioning) ---

    def get_state(self, address: int) -> bytes:
        """
        [Code 10] MP_Get_State: Lit l'état étendu (Emergency, Adaption active, etc.).
        Retourne 7 octets de status.
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_STATE, [])
        return self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_mp_address(self, address: int) -> int:
        """[Code 13] MP_Get_MP_Address: Lit l'adresse MP programmée."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_MP_ADDRESS, [])
        data_bytes = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        return data_bytes[0] if data_bytes else 0

    def start_adaption(self, address: int, choice: int) -> None:
        """
        [Code 33] MP_Start_Adaption: Lance une séquence.
        choice: 0x55=Adaption, 0xAA=Sync, 0x61=Testrun.
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_START_ADAPTION, [choice])
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def set_mp_address(self, serial_data: bytes, old_address: int, new_address: int) -> bool:
        """
        [Code 38] MP_Set_MP_Address: Ré-adressage (Mode Broadcast obligatoire).
        """
        if len(serial_data) != 7:
            raise ValueError("Le serial_data doit être de 7 octets.")

        # Protection EEPROM basique via cache
        if (old_address, serial_data) in self.address_cache and old_address == new_address:
            self.logger.info(f"Adressage ignoré (Déjà fait pour ce numéro de série).")
            return True

        params = list(serial_data) + [new_address]
        # Commande broadcast pour éviter les collisions
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_BROADCAST, 0, self.MP_CMD_SET_MP_ADDRESS, params)

        self.logger.info(f"Broadcast SET_MP_ADDRESS {new_address} pour SN {serial_data.hex()}")
        self.controller.send_command(cmd, MPUtils.MP_MODE_BROADCAST, old_address)

        # Validation obligatoire : on essaie de lire le numéro de série sur la nouvelle adresse
        try:
            new_serial = self.get_series_no(new_address)
            if new_serial == serial_data:
                if (old_address, serial_data) not in self.address_cache:
                     self.address_cache.append((new_address, serial_data))
                return True
        except MPBusErrorException:
            pass
        return False

    def get_series_no(self, address: int) -> bytes:
        """[Code 50] MP_Get_SeriesNo: Lit le numéro de série (7 octets)."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_SERIES_NO, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        return resp

    def start_testrun_fire(self, address: int, choice: int) -> None:
        """
        [Code 86] MP_Start_Testrun_Fire: Specifique clapets feu.
        choice: 0x61=FireTest, 0x62=FreeDamperTest.
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_START_TEST_FIRE, [choice])
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def set_bus_watchdog(self, address: int, bus_zf: int) -> None:
        """
        [Code 91] MP_Set_BusWatchdog: Définit la position de repli en cas de perte bus.
        bus_zf: Même codes que Set_Forced (0=Disabled).
        """
        self.logger.warning("Écriture Configuration (Watchdog) : Attention EEPROM.")
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_WATCHDOG, [bus_zf])
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_bus_watchdog(self, address: int) -> int:
        """[Code 92] MP_Get_BusWatchdog: Lit le réglage watchdog."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_WATCHDOG, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        return resp[0] if resp else 0

    def set_special_functions(self, address: int, func: int) -> None:
        """
        [Code 102] MP_Set_Special_Functions: Comportement LED.
        0=WiringOK, 1=Blink Addr, 2=Always On, 3=Always Off.
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_SPECIAL, [func])
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    # --- 6.4 Monitoring ---

    def get_stress(self, address: int) -> Tuple[int, int, int]:
        """
        [Code 11] MP_Get_Stress: Lit les compteurs de vie.
        Retourne (OpTime [h], ActiveTime [h], Utilisation [%]).
        """
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_STRESS, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 6:
            raise MPProtocolError("Réponse MP_Get_Stress trop courte.")
        # OpTime (unit 4h), ActiveTime (1h).
        op_time_raw = self._bytes_to_int(resp[0:2])
        active_time = self._bytes_to_int(resp[2:4])
        util = self._bytes_to_int(resp[4:6])
        return op_time_raw * 4, active_time, util

    def get_malfunction_mask(self, address: int) -> Tuple[int, int]:
        """[Code 24] MP_Get_Malfunction_Maintenance_Mask: Retourne (MalfMask, MaintMask)."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_MASK, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        return resp[0], resp[1]

    def get_error_state(self, address: int) -> int:
        """[Code 26] MP_Get_Malfunction_Maintenance_State: Retourne l'état des erreurs."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_ERR_STATE, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        return resp[0]

    def reset_error_state(self, address: int, mask: int) -> None:
        """[Code 29] MP_Reset_Malfunction_Maintenance_State: Acquitte les erreurs."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_RESET_ERR, [mask])
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    # --- 6.5 Configuration (Attention EEPROM !) ---

    def set_ext_event(self, address: int, events: List[int]) -> None:
        """
        [Code 15] MP_Set_Ext_Event: Config boutons/power-on.
        Attention: Commande de configuration (EEPROM).
        """
        self.logger.warning("Écriture Configuration (Ext Event) : Attention EEPROM.")
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_EXT_EVENT, events)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def set_transit_time(self, address: int, time_sec: int) -> None:
        """[Code 46] MP_Set_Transit_Time: Config temps de course (EEPROM)."""
        self.logger.warning("Écriture Configuration (Transit Time) : Attention EEPROM.")
        params = self._int_to_bytes(time_sec, 2)
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_TRANSIT_TIME, params)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def set_operating_range(self, address: int, rng: int) -> None:
        """[Code 58] MP_Set_Operating_Range: Config course mécanique (EEPROM)."""
        self.logger.warning("Écriture Configuration (Op Range) : Attention EEPROM.")
        params = self._int_to_bytes(rng, 2)
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_OP_RANGE, params)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def set_min_mid_max(self, address: int, mn: int, mid: int, mx: int) -> None:
        """[Code 61] MP_Set_Min_Mid_Max: Config limites (EEPROM)."""
        self.logger.warning("Écriture Configuration (Min/Mid/Max) : Attention EEPROM.")
        params = self._int_to_bytes(mn, 2) + self._int_to_bytes(mid, 2) + self._int_to_bytes(mx, 2)
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_MIN_MID_MAX, params)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def set_sync(self, address: int, direction: int) -> None:
        """
        [Code 65] MP_Set_Sync: Config direction de synchro (EEPROM).
        0x55=Open, 0xAA=Close.
        """
        self.logger.warning("Écriture Configuration (Sync) : Attention EEPROM.")
        params = [0, direction] # Byte 1 reserved
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_SYNC, params)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_ext_event(self, address: int, ident: int = 0x01) -> List[int]:
        """[Code 69] MP_Get_Ext_Event: Lit config boutons."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_EXT_EVENT, [ident])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        return list(resp)

    def get_string_address(self, address: int) -> Tuple[int, int, int]:
        """[Code 71] MP_Get_String_Adr: Lit adresses mémoires des strings."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_STR_ADDR, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 6:
            raise MPProtocolError("Réponse MP_Get_String_Adr trop courte.")
        oem = self._bytes_to_int(resp[0:2])
        pos = self._bytes_to_int(resp[2:4])
        bel = self._bytes_to_int(resp[4:6])
        return oem, pos, bel

    def login(self, address: int, password: bytes) -> bool:
        """[Code 78] MP_Login: Authentification pour commandes protégées."""
        if len(password) != 4:
            raise ValueError("Mot de passe doit être 4 octets.")
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_LOGIN, list(password))
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        return True

    def get_firmware(self, address: int) -> Tuple[int, int]:
        """[Code 82] MP_Get_Firmware: Retourne (Major, Minor)."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_FIRMWARE, [])
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) < 2: return 0,0
        return resp[0], resp[1]

    # --- 6.6 Data Pool Handling ---

    def set_data(self, address: int, data_id: int, value: Union[int, bytes, List[int]]) -> int:
        """
        [Code 110] MP_Set_Data: Ecrit jusqu'à 4 octets dans l'ID spécifié.
        Retourne 'more' (nombre d'octets restants attendus par l'esclave).
        """
        data_bytes = []
        if isinstance(value, int):
             if value < 256: data_bytes = [value]
             elif value < 65536: data_bytes = self._int_to_bytes(value, 2)
             else: data_bytes = self._int_to_bytes(value, 4)
        elif isinstance(value, (bytes, list)):
            data_bytes = list(value)

        if len(data_bytes) > 4:
            raise ValueError("MP_Set_Data supporte max 4 octets.")

        params = self._int_to_bytes(data_id, 2) + data_bytes
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_DATA, params)

        # Reponse vide ou [more]
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)
        if len(resp) > 0:
            return resp[0] # 'more' bytes needed
        return 0

    def get_data(self, address: int, data_id: int) -> Tuple[bytes, int]:
        """
        [Code 111] MP_Get_Data: Lit une valeur depuis le Data Pool.
        Retourne (DataBytes, MoreBytesAvailable).
        """
        params = self._int_to_bytes(data_id, 2)
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_DATA, params)
        resp = self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

        # Format réponse: Data[1..4] ou Data[1..4] + More[1]
        data = resp
        more = 0
        if len(resp) == 5:
            data = resp[:-1]
            more = resp[-1]

        return data, more

    def set_next_block(self, address: int, block_no: int, data: bytes) -> None:
        """[Code 112] MP_Set_NextBlock: Ecriture suite données (Data Pool)."""
        if len(data) > 5:
             raise ValueError("NextBlock data max 5 bytes.")
        params = [block_no] + list(data)
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_SET_NEXTBLOCK, params)
        self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)

    def get_next_block(self, address: int, block_no: int) -> bytes:
        """[Code 113] MP_Get_NextBlock: Lecture suite données (Data Pool)."""
        cmd = MPUtils.build_mp_frame(MPUtils.MP_MODE_ADDRESSED, address, self.MP_CMD_GET_NEXTBLOCK, [block_no])
        return self.controller.send_command(cmd, MPUtils.MP_MODE_ADDRESSED, address)




import logging

# 1. Configurer le Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("MPMaster")

# 2. Configurer le Transport (Gateway TCP)
# Remplacez l'IP et le Port par ceux de votre gateway MP-Bus <-> TCP
wrapper = TCPGatewayWrapper(host="192.168.0.227", port=5000, gateway_id=1, logger=logger)
wrapper.connect()
transport = MPBusTransport(wrapper)

# 3. Initialiser le Contrôleur et l'API
controller = MPBusMasterController(transport, logger)
api = MPBusAPI(controller, logger)

try:
    # 4. Exécuter des commandes

    # Lire le numéro de série (Actionneur adresse 1)
    serial = api.get_series_no(address=1)
    print(f"Serial Number: {serial.hex()}")

    # Déplacer à 50%
    api.set_relative(address=1, setpoint=5000) # 50.00%

    # Lire la position actuelle
    pos, setp = api.get_relative(address=1)
    print(f"Position: {pos/100}%, Consigne: {setp/100}%")

except Exception as e:
    print(f"Erreur: {e}")

finally:
    wrapper.close()


