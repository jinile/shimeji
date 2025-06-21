
import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QTimer, QSize, Qt, QPoint, QDateTime

class Shimeji(QMainWindow):
    instances = []

    @classmethod
    def add_instance(cls):
        if len(cls.instances) < 5:
            instance = Shimeji()
            instance.show()
            cls.instances.append(instance)

    @classmethod
    def remove_instance(cls):
        if len(cls.instances) > 1:
            instance = cls.instances.pop()
            instance.close()

    def __init__(self):
        super().__init__()

        # Initialize the user interface
        self.initUI()
    
    def initUI(self):
        # Set the window title
        self.setWindowTitle('Shimeji')

        # Get screen dimensions
        screen_size = QApplication.desktop().screenGeometry()

        # Set window geometry to cover the entire screen
        self.setGeometry(screen_size)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create a QLabel to display the Shimeji image
        self.label = QLabel(self)
        self.image_paths_idle = [
            'MakotoStandLeft.png',
            'MakotoStandRight.png',
            'MakotoSitAngry.png'
            # Add more idle image paths as needed
        ]
        self.image_paths_walk_left = [
            'MakotoWalkLeft1.png',
            'MakotoWalkLeft2.png',
            # Add more walk left image paths as needed
        ]
        self.image_paths_walk_right = [
            'MakotoWalkRight1.png',
            'MakotoWalkRight2.png',
            # Add more walk right image paths as needed
        ]
        self.image_paths_jump = [
            'MakotoJump1.png',
            'MakotoJump2.png'
            # Add more jump image paths as needed
        ]
        self.image_dragging_left_slow = 'MakotoDragLeftSlow.png'  # Image path for dragging left slow state
        self.image_dragging_right_slow = 'MakotoDragRightSlow.png'  # Image path for dragging right slow state
        self.image_dragging_left_fast = 'MakotoDragLeftFast.png'  # Image path for dragging left fast state
        self.image_dragging_right_fast = 'MakotoDragRightFast.png'  # Image path for dragging right fast state
        self.image_fall_left = 'MakotoFallLeft.png'  # Image path for falling left state
        self.image_fall_right = 'MakotoFallRight.png'  # Image path for falling right state
        self.image_faceplant_right = 'MakotoFaceplantRight.png'  # Image path for faceplant right state

        self.current_animation = self.image_paths_walk_left  # Start with walking left
        self.animation_index = 0  # Track the index of the current animation image

        pixmap = QPixmap(self.current_animation[self.animation_index])
        pixmap = pixmap.scaled(QSize(300, 300))  # Resize the pixmap
        self.label.setPixmap(pixmap)
        self.label.setGeometry(0, 0, pixmap.width(), pixmap.height())

        # Set initial position
        self.label.move(0, self.height() - self.label.height())

        # Create a QTimer to update the shimeji image
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateShimeji)  # Connect the timer to the updateShimeji function
        self.timer.start(100)  # Set the timer interval (in milliseconds)

        # Enable mouse tracking to track mouse movement even without clicking
        self.setMouseTracking(True)

        # Variables to store mouse position and speed
        self.last_mouse_pos = QPoint()
        self.last_mouse_time = QDateTime.currentDateTime()

        # Variables to store dragging state
        self.dragging = False
        self.offset = QPoint()

        # Variables for falling animation
        self.falling = False
        self.fall_speed = 75  # Adjust this value to change the falling speed

        # Variables for jumping animation sequence
        self.jumping = False
        self.jump_count = 0

        # Probability of standing idle while walking (in percent)
        self.idle_probability = 1  # Adjust this value as needed

        # Variable to store the current idle image index
        self.idle_image_index = 0

        # List of possible texts to display
        self.texts = ["Isn't that right, HARRY", "Anytime I talk to him, I need to be prepared for extreme psychological trauma.",
         "I love you, Harry!", "You’re so full of… SHIT!!" , "It's Naeging Time!", 
         "If all hope is fading, we just need to become the NEW hope", "It's okay, I fall into total despair when west ham loses too"]

    def updateShimeji(self):
        if not self.dragging:
            if self.falling:
                # Update position for falling animation
                new_y = self.label.y() + self.fall_speed
                if new_y + self.label.height() >= self.height():
                    # Stop falling animation when reached bottom of the screen
                    new_y = self.height() - self.label.height()
                    self.falling = False
                    # Change to faceplant image
                    faceplant_pixmap = QPixmap(self.image_faceplant_right)
                    faceplant_pixmap = faceplant_pixmap.scaled(QSize(300, 300))  # Resize the pixmap
                    self.label.setPixmap(faceplant_pixmap)
                    # Wait for 2 seconds before resuming walking
                    QTimer.singleShot(2000, self.resumeWalking)
                else:
                    # Initialize falling_pixmap
                    falling_pixmap = None
                    # Update the shimeji image during falling animation
                    if self.current_animation == self.image_paths_walk_left:
                        falling_pixmap = QPixmap(self.image_fall_left)
                    elif self.current_animation == self.image_paths_walk_right:
                        falling_pixmap = QPixmap(self.image_fall_right)
                    if falling_pixmap:
                        falling_pixmap = falling_pixmap.scaled(QSize(300, 300))  # Resize the pixmap
                        self.label.setPixmap(falling_pixmap)
                self.label.move(self.label.x(), new_y)
            elif not self.jumping:
                # Update the shimeji image during normal animation
                if self.current_animation == self.image_paths_idle:
                    # If idle, do not update the image or move
                    return
                self.animation_index = (self.animation_index + 1) % len(self.current_animation)
                pixmap = QPixmap(self.current_animation[self.animation_index])
                pixmap = pixmap.scaled(QSize(300, 300))  # Resize the pixmap
                self.label.setPixmap(pixmap)

                # Move the shimeji horizontally
                new_x = self.label.x() + 10 if self.current_animation == self.image_paths_walk_right else self.label.x() - 10
                self.label.move(new_x, self.label.y())

                # Check if the shimeji reached the left or right edge of the screen
                if self.label.x() <= 0:
                    self.current_animation = self.image_paths_walk_right
                elif self.label.x() + self.label.width() >= self.width():
                    self.current_animation = self.image_paths_walk_left

                # Check if the shimeji is walking along the bottom of the screen and trigger idle animation randomly
                if self.label.y() + self.label.height() >= self.height():
                    if random.randint(1, 100) <= self.idle_probability:
                        self.current_animation = self.image_paths_idle
                        # Select a random idle image
                        self.idle_image_index = random.randint(0, len(self.image_paths_idle) - 1)
                        idle_pixmap = QPixmap(self.image_paths_idle[self.idle_image_index])
                        idle_pixmap = idle_pixmap.scaled(QSize(300, 300))  # Resize the pixmap
                        self.label.setPixmap(idle_pixmap)
                        # Start idle timer
                        QTimer.singleShot(3000, self.resumeWalking)  # Change idle duration to 3 seconds

            # Random chance for text to appear
            if random.random() < 0.007:
                text = random.choice(self.texts)
                self.showTextAboveShimeji(text)

    def showTextAboveShimeji(self, text):
        # Create a QLabel to display the text above the shimeji
        label = QLabel(self)
        label.setFont(QFont("Arial", 12, QFont.Bold))
        label.setText(text)
        label.adjustSize()

    # Calculate the position of the label
        label_x = int(self.label.mapTo(self, QPoint(0, -label.height())).x() + (self.label.width() - label.width()) / 2)
        label_y = int(self.label.mapTo(self, QPoint(0, -label.height())).y()) - label.height()

    # Set the position of the label
        label.move(label_x, label_y)
        label.show()

    # Create additional labels to display white outlines
        outline_offsets = [(2, 0), (-2, 0), (0, 2), (0, -2)]  # Adjust these offsets as needed for the outline effect
        outline_labels = []
        for dx, dy in outline_offsets:
            outline_label = QLabel(self)
            outline_label.setFont(QFont("Arial", 12, QFont.Bold))
            outline_label.setText(text)
            outline_label.adjustSize()
            outline_label.setStyleSheet("color: white;")  # Set the text color to white
            outline_label.move(label_x + dx, label_y + dy)
            outline_label.show()
            outline_labels.append(outline_label)

    # Remove the labels after a certain time
        QTimer.singleShot(3000, lambda: [label.deleteLater() for label in outline_labels + [label]])


    def resumeWalking(self):
        # Resume walking animation after idle
        self.current_animation = self.image_paths_walk_left if self.current_animation == self.image_paths_idle else self.image_paths_walk_right

    def mousePressEvent(self, event):
        # Check if the mouse press event occurred within the shimeji label
        if event.button() == Qt.RightButton and self.label.geometry().contains(event.pos()):
            # Start jumping animation if right-clicked while walking
            if not self.jumping and (self.current_animation == self.image_paths_walk_left or self.current_animation == self.image_paths_walk_right):
                self.startJumpingAnimation()
        elif event.button() == Qt.LeftButton and self.label.geometry().contains(event.pos()):
            # Enable dragging
            self.dragging = True
            # Calculate offset from mouse click to top-left corner of the label
            self.offset = event.pos() - self.label.pos()

    def startJumpingAnimation(self):
        # Start the jumping animation sequence
        self.jumping = True
        self.jump_count = 0
        self.timer_jump = QTimer(self)
        self.timer_jump.timeout.connect(self.animateJump)  # Connect the timer to the animateJump function
        self.timer_jump.start(500)  # Set the timer interval for each jump (in milliseconds)

    def animateJump(self):
        # Animate the jumping sequence
        jump_index = self.jump_count % len(self.image_paths_jump)
        jump_pixmap = QPixmap(self.image_paths_jump[jump_index])
        jump_pixmap = jump_pixmap.scaled(QSize(300, 300))  # Resize the pixmap
        self.label.setPixmap(jump_pixmap)
        self.jump_count += 1
        # Stop jumping animation after three jumps
        if self.jump_count >= 6:  # Adjust the number of jumps as needed
            self.timer_jump.stop()
            self.jumping = False
            # Resume walking animation after jumping
            QTimer.singleShot(2000, self.resumeWalking)

    def mouseMoveEvent(self, event):
        if self.dragging:
            # Update position of the label based on mouse movement
            self.label.move(event.pos() - self.offset)
            # Determine dragging direction and speed
            current_time = QDateTime.currentDateTime()
            time_diff = self.last_mouse_time.msecsTo(current_time)
            if time_diff > 0:
                speed = (event.pos() - self.last_mouse_pos).manhattanLength() / time_diff
                if event.x() > self.last_mouse_pos.x():
                    if speed > 1:  # Adjust the speed threshold as needed
                        dragging_pixmap = QPixmap(self.image_dragging_right_fast)
                    else:
                        dragging_pixmap = QPixmap(self.image_dragging_right_slow)
                else:
                    if speed > 1:  # Adjust the speed threshold as needed
                        dragging_pixmap = QPixmap(self.image_dragging_left_fast)
                    else:
                        dragging_pixmap = QPixmap(self.image_dragging_left_slow)
                dragging_pixmap = dragging_pixmap.scaled(self.label.size())  # Scale dragging pixmap to match label size
                self.label.setPixmap(dragging_pixmap)
            self.last_mouse_pos = event.pos()
            self.last_mouse_time = current_time

    def mouseReleaseEvent(self, event):
        # Disable dragging when mouse button is released
        self.dragging = False
        # Start falling animation
        self.falling = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus:
            Shimeji.add_instance()
        elif event.key() == Qt.Key_Minus:
            Shimeji.remove_instance()

def main():
    app = QApplication(sys.argv)
    shimeji = Shimeji()  # Create an instance of the Shimeji class
    shimeji.show()  # Display the main window
    Shimeji.instances.append(shimeji)
    app.aboutToQuit.connect(app.deleteLater)  # Ensures proper cleanup
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
