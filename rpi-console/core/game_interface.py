"""
Interface Base Abstrata para os Jogos do Tech Arcade Console.
Seguindo os princípios SOLID:
- Interface Segregation e Single Responsibility
- Ciclo de vida padronizado para execução modular na engine Pygame
"""

from abc import ABC, abstractmethod
import pygame


class Jogo(ABC):
    """
    Classe base para todos os jogos integrados ao console.
    Define o contrato de ciclo de vida e renderização para a resolução 1024x600.
    """

    @abstractmethod
    def get_id(self) -> str:
        """Retorna o identificador único do jogo."""
        pass

    @abstractmethod
    def get_nome(self) -> str:
        """Retorna o nome exibido no menu/launcher."""
        pass

    @abstractmethod
    def get_descricao(self) -> str:
        """Retorna uma breve descrição das regras do jogo."""
        pass

    @abstractmethod
    def iniciar(self) -> None:
        """Inicializa ou reseta o estado do jogo ao entrar."""
        pass

    @abstractmethod
    def processar_eventos(self, eventos_pygame: list[pygame.event.Event], estado_botoes: dict[str, bool]) -> None:
        """
        Recebe tanto os eventos de toque/mouse do Pygame quanto
        os estados dos botões físicos da GPIO.
        """
        pass

    @abstractmethod
    def atualizar(self, dt: float) -> None:
        """Atualiza a lógica interna e temporizadores não-bloqueantes com base no delta-time."""
        pass

    @abstractmethod
    def renderizar(self, superficie: pygame.Surface) -> None:
        """Renderiza a interface do jogo diretamente na superfície 1024x600."""
        pass

    @abstractmethod
    def encerrar(self) -> None:
        """Desliga atuadores, cancela timers e limpa recursos antes de voltar ao menu."""
        pass

    @abstractmethod
    def solicitou_retorno(self) -> bool:
        """Indica se o jogador pediu para retornar ao menu principal."""
        pass
