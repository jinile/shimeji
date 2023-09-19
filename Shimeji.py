import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDesktopWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QPoint, Qt

class Shimeji(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the user interface
        self.initUI()
    
    def initUI(self):
        # Set the window title and initial geometry
        self.setWindowTitle('Shimeji')
        self.setGeometry(100, 100, 1920, 1080)
        self.centerWindow()  # Center the window on the screen

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create a QLabel to display the Shimeji image
        self.label = QLabel(self)
        self.image_paths_idle = [
            'c:\\Users\\jeann\\OneDrive\\Pictures\\MammonShimeji\\Mammon1.png',
            # Add more idle image paths as needed
        ]
        self.image_paths_left = [
            'c:\\Users\\jeann\\OneDrive\\Pictures\\MammonShimeji\\Mammon2.png',
            'c:\\Users\\jeann\\OneDrive\\Pictures\\MammonShimeji\\Mammon3.png',
            # Add more left movement image paths as needed
        ]
        self.image_paths_right = [
            'c:\\Users\\jeann\\OneDrive\\Pictures\\MammonShimeji\\MammonRight2.png',
            'c:\\Users\\jeann\\OneDrive\\Pictures\\MammonShimeji\\MammonRight3.png',
            # Add more right movement image paths as needed
        ]
        self.image_paths_dragged = [
            'c:\\Users\\jeann\\OneDrive\\Pictures\\MammonShimeji\\Mammon6.png',
            # Add more dragged image paths as needed
        ]
        self.image_paths_dropped = [
            'c:\\Users\\jeann\\OneDrive\\Pictures\\MammonShimeji\\Mammon4.png',
            # Add more dropped image paths as needed
        ]
        
        self.idle_image_index = 0
        self.dragged_image_index = 0
        self.dropped_image_index = 0
        self.left_image_index = 0
        self.right_image_index = 0
        self.idle = True  # Track whether the Shimeji is idle or dragged

        pixmap = QPixmap(self.image_paths_idle[self.idle_image_index])
        self.label.setPixmap(pixmap)
        self.label.setGeometry(0, 0, pixmap.width(), pixmap.height())

        # Create a QTimer to control Shimeji movement animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.moveShimeji)  # Connect the timer to the moveShimeji function
        self.timer.start(50)  # Set the timer interval (in milliseconds)

        # Initialize the movement direction
        self.direction = QPoint(1, 1)

        # Variables for handling dragging
        self.dragging = False
        self.offset = QPoint()

        self.dropping = False

        # Variables for the vertical drop effect
        self.vertical_position = 0
        self.vertical_velocity = 0
        self.gravity = 1  # Adjust this value for the desired gravity effect

    def centerWindow(self):
        # Calculate the window position to center it on the screen
        frame = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    def moveShimeji(self):
        # Get the current position of the QLabel
        current_pos = self.label.pos()

        # Calculate the new horizontal position based on the X-axis direction
        new_x = current_pos.x() + self.direction.x()

        # Check for collisions with the left and right screen edges
        if (
            new_x < 0
            or new_x + self.label.width() > self.width()
        ):
            # Reverse the X-axis direction if the Shimeji is about to move out of bounds
            self.direction.setX(-self.direction.x())

        # Update the horizontal position of the QLabel (only horizontal movement)
        self.label.move(new_x, current_pos.y())

        # Handle the vertical drop effect when not dragging
        if not self.dragging:
            self.vertical_velocity += self.gravity  # Apply gravity
            new_y = current_pos.y() + self.vertical_velocity
            # Check for collisions with the bottom screen edge
            if new_y + self.label.height() > self.height():
                new_y = self.height() - self.label.height()
                self.vertical_velocity = 0  # Reset velocity on ground contact
                if self.dropping:
                    self.dropping = False
                    self.toggleImage()  # Call toggleImage when the drop is complete
            self.label.move(self.label.pos().x(), new_y)

        # Change the image when idle
         # Change the image based on direction and idle state
        if self.dragging:
            self.toggleImage()  # Call toggleImage to switch to left or right image

        elif self.dropping:
            self.toggleImage()  # Call toggleImage when dropping

        else:
            if self.direction.x() < 0:
                self.idle_image_index = (self.idle_image_index + 1) % len(self.image_paths_left)
                pixmap = QPixmap(self.image_paths_left[self.idle_image_index])
            elif self.direction.x() > 0:
                self.idle_image_index = (self.idle_image_index + 1) % len(self.image_paths_right)
                pixmap = QPixmap(self.image_paths_right[self.idle_image_index])
            else:
                self.idle_image_index = (self.idle_image_index + 1) % len(self.image_paths_idle)
                pixmap = QPixmap(self.image_paths_idle[self.idle_image_index])
            self.label.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos() - self.label.pos()
            self.dragging = True
            self.toggleImage()  # Call toggleImage when the mouse is pressed

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.label.move(event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.dropping = True
            self.toggleImage()  # Call toggleImage when the mouse is released
            # Set the initial vertical velocity for the drop effect
            self.vertical_velocity = 2  # Adjust this value for the desired drop speed
            
    def toggleImage(self):
        # Toggle between idle, dragged, and dropped images
        if self.dragging:
            self.dragged_image_index = (self.dragged_image_index + 1) % len(self.image_paths_dragged)
            pixmap = QPixmap(self.image_paths_dragged[self.dragged_image_index])
            self.label.setPixmap(pixmap)
            self.idle = False
        elif self.dropping:
            self.dropped_image_index = (self.dropped_image_index + 1) % len(self.image_paths_dropped)
            pixmap = QPixmap(self.image_paths_dropped[self.dropped_image_index])
            self.label.setPixmap(pixmap)
            self.idle = False
        else:
            self.idle_image_index = (self.idle_image_index + 1) % len(self.image_paths_idle)
            pixmap = QPixmap(self.image_paths_idle[self.idle_image_index])
            self.label.setPixmap(pixmap)
            self.idle = True

def main():
    app = QApplication(sys.argv)
    shimeji = Shimeji()  # Create an instance of the Shimeji class
    shimeji.show()  # Display the main window
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
